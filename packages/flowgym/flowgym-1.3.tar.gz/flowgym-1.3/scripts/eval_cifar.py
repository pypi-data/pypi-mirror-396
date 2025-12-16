r"""Run value matching on specified environment and method.

Example usage:
```
python eval_value_matching.py --dir ./experiments/value_matching --ckpt last.ckpt
```
"""

import argparse
import math
import os
import random

import numpy as np
import open_clip
import torch
import yaml
from flowgym.methods.value_matching import ValuePolicy
from PIL import Image
from torcheval.metrics import FrechetInceptionDistance
from torchvision import transforms
from torchvision.utils import save_image
from tqdm import tqdm, trange
from vendi_score import vendi

import flowgym

from .run_value_matching import get_value_network


@torch.no_grad()
def main(args):
    """Evaluate value matching."""
    if args.seed is not None:
        torch.manual_seed(args.seed)
        np.random.seed(args.seed)
        random.seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with open(os.path.join(args.dir, "args.yaml"), "r") as f:
        train_args = yaml.safe_load(f)

    env = flowgym.make(
        train_args["base_model"],
        train_args["reward"],
        train_args["num_steps"],
        reward_scale=1,
        # train_args["reward_scale"],
        device=device,
        base_model_kwargs=train_args["base_model_kwargs"],
        reward_kwargs=train_args["reward_kwargs"]
    )

    if args.ckpt is not None:
        if "depth" in train_args and "width" in train_args:
            value_network = get_value_network(
                train_args["base_model"],
                train_args["depth"],
                train_args["width"],
                train_args["reward_scale"],
            ).to(device)
            value_network.load_state_dict(
                torch.load(
                    os.path.join(args.dir, "checkpoints", args.ckpt),
                    map_location=device,
                )
            )
            value_network.eval()
            control = ValuePolicy(value_network, env.memoryless_schedule)
            env.control_policy = control
        else:
            env.base_model.load_state_dict(
                torch.load(
                    os.path.join(args.dir, "checkpoints", args.ckpt),
                    map_location=device,
                )
            )

    env.base_model.eval()

    # Make dir for samples
    sample_dir = None
    if args.sample_dir is not None:
        sample_dir = os.path.join(args.dir, args.sample_dir)
        os.makedirs(sample_dir, exist_ok=True)

    rewards = torch.zeros(args.num_samples)
    image_tensors = []

    pbar = tqdm(batch_indices(args.num_samples, args.batch_size))
    for head, tail in pbar:
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            samples, _, _, _, _, r, _, _, _ = env.sample(
                tail - head,
                pbar=False,
            )

        image_tensors.append(samples)

        for i in range(tail - head):
            if sample_dir is not None:
                save_image(samples[i].unsqueeze(0), os.path.join(sample_dir, f"{head+i:06d}.png"))

        rewards[head:tail] = r.squeeze().cpu()
        pbar.set_postfix(
            r_mean=rewards[:tail].mean().item(),
            r_std=rewards[:tail].std().item(),
        )

    print(f"Reward: {rewards.mean().item():.4f} ± {rewards.std().item():.4f}")

    image_tensors = torch.cat(image_tensors, dim=0).to(device)
    base_samples = torch.load("cifar_base_samples.pt", map_location=device)
    print(f"FID: {fid(image_tensors, base_samples, device):.4f}")

    image_tensors = image_tensors.cpu()
    clip_feats = clip_features(image_tensors, device).cpu()

    print(f"Vendi (clip): {vendi.score_dual(clip_feats, q=0.5):.4f}")  # type: ignore
    print(f"Vendi (pixel): {vendi.score_dual(image_tensors.flatten(start_dim=1), q=0.5):.4f}")  # type: ignore


@torch.no_grad()
def clip_features(samples: torch.Tensor, device: torch.device, batch_size=256) -> torch.Tensor:
    clip, _, _ = open_clip.create_model_and_transforms("ViT-L-14", pretrained="openai", device=device)
    preprocess = transforms.Compose([
        transforms.Resize(224, interpolation=Image.BICUBIC, max_size=None, antialias=True),  # type: ignore
        transforms.CenterCrop(224),
        transforms.Normalize(mean=(0.48145466, 0.4578275, 0.40821073), std=(0.26862954, 0.26130258, 0.27577711)),
    ])
    clip.eval()  # type: ignore

    num_samples = samples.shape[0]
    features = torch.zeros(num_samples, 768, device=device)
    for head, tail in tqdm(batch_indices(num_samples, batch_size), desc="computing clip features"):
        batch = samples[head:tail].to(device)
        batch = preprocess(batch).to(device)
        feat = clip.encode_image(batch)  # type: ignore
        feat = feat / feat.norm(dim=-1, keepdim=True)
        features[head:tail] = feat

    return features


@torch.no_grad()
def fid(samples1: torch.Tensor, samples2: torch.Tensor, device: torch.device, batch_size=256) -> float:
    """
    Computes the Frechet Inception Distance (FID) between two sets of image samples.
    
    Args:
        samples1 (Tensor): First set of samples.
        samples2 (Tensor): Second set of samples.
        device (torch.device): Device to perform computations on.
        batch_size (int): Number of samples to process in each batch.

    Returns
    -------
        float: The computed FID score.
    
    """
    num_samples = min(samples1.shape[0], samples2.shape[0])
    fid = FrechetInceptionDistance(device=device)
    for i in trange(math.ceil(num_samples / batch_size), desc="Computing FID"):
        head = i * batch_size
        tail = min(head + batch_size, num_samples)
        fid.update(samples1[head:tail], is_real=True)
        fid.update(samples2[head:tail], is_real=False)

    return fid.compute().item()


class batch_indices:
    def __init__(self, total, batch_size):
        if total < 0 or batch_size <= 0:
            raise ValueError("total must be non-negative and batch_size must be positive")
        self.total = total
        self.batch_size = batch_size
        self._num_batches = math.ceil(self.total / self.batch_size)

    def __len__(self):
        """Returns the total number of batches."""
        return self._num_batches

    def __getitem__(self, index):
        """Returns the (start, end) pair for a given batch index."""
        # Handle negative indexing like lists do
        if index < 0:
            index += self._num_batches

        if not 0 <= index < self._num_batches:
            raise IndexError("Batch index out of range")

        start = index * self.batch_size
        end = min(start + self.batch_size, self.total)
        return start, end

    def __iter__(self):
        """Allows the object to be used in a for loop."""
        for i in range(len(self)):
            yield self[i]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate value matching")
    parser.add_argument("--dir", type=str, required=True, help="Experiment directory")
    parser.add_argument("--sample_dir", type=str, default=None, help="Directory in --dir to save samples")
    parser.add_argument("--ckpt", type=str, default=None, help="Loads the weights in dir/checkpoints/<ckpt>")
    parser.add_argument("--num_steps", type=int, default=100, help="Number of timesteps to discretize the SDE")
    parser.add_argument("--num_samples", type=int, default=1_000, help="Number of samples to estimate the expectation.")
    parser.add_argument("--batch_size", type=int, default=256, help="Batch size for sampling")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    args = parser.parse_args()
    main(args)
