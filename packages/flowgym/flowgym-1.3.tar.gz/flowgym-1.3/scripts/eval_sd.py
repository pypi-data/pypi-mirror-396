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

import hpsv2
import numpy as np
import open_clip
import torch
import yaml
from dreamsim import dreamsim
from flowgym.utils import ValuePolicy
from PIL import Image
from torchvision.transforms.functional import to_pil_image
from torchvision.utils import save_image
from tqdm import tqdm
from transformers import AutoModel, AutoProcessor

import flowgym
from flowgym import ConstantNoiseSchedule

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
        train_args["reward_scale"],
        device=device,
        base_model_kwargs=train_args["base_model_kwargs"],
        reward_kwargs=train_args["reward_kwargs"]
    )

    env.base_model = env.base_model.to(dtype=torch.bfloat16)
    # env.scheduler.noise_schedule = ConstantNoiseSchedule(0)

    if args.ckpt is not None:
        value_network = get_value_network(
            train_args["base_model"],
            train_args["reward"],
            train_args["depth"],
            train_args["width"],
            train_args["reward_scale"],
        ).to(device)

        state_dict = torch.load(os.path.join(args.dir, "checkpoints", args.ckpt))
        value_network.load_state_dict(state_dict)

        value_network = value_network.to(device, dtype=torch.bfloat16)

        control = ValuePolicy(value_network, env.memoryless_schedule)
        env.control_policy = control

    # Make dir for samples
    sample_dir = os.path.join(args.dir, args.sample_dir)
    os.makedirs(sample_dir, exist_ok=True)

    if args.prompt is not None:
        prompts_list = [args.prompt] * args.num_samples
    else:
        prompts_list = random.sample(env.base_model.prompts, args.num_samples)

    rewards = torch.zeros(args.num_samples)
    images_list = []

    pbar = tqdm(batch_indices(args.num_samples, args.batch_size))
    for head, tail in pbar:
        prompt = prompts_list[head:tail]
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            samples, _, _, _, _, r, _, _, _ = env.sample(
                tail - head,
                pbar=False,
                prompt=prompt,
                cfg_scale=args.cfg_scale,
            )

        for i in range(tail - head):
            save_image(samples[i].unsqueeze(0), os.path.join(sample_dir, f"{head+i:06d}.png"))
            images_list.append(to_pil_image(samples[i].to(dtype=torch.float)))

        rewards[head:tail] = r.squeeze().cpu()
        pbar.set_postfix(
            r_mean=rewards[:tail].mean().item(),
            r_std=rewards[:tail].std().item(),
        )

    print(f"Reward: {rewards.mean().item():.4f} ± {rewards.std().item():.4f}")

    # clip_mean, clip_std = clip_score(images_list, prompts_list, device)
    # print(f"CLIP Score: {clip_mean:.4f} ± {clip_std:.4f}")

    # pick_mean, pick_std = pick_score(images_list, prompts_list, device)
    # print(f"Pick Score: {pick_mean:.4f} ± {pick_std:.4f})")

    # hps_mean, hps_std = human_preference_score(images_list, prompts_list)
    # print(f"HPS Score: {hps_mean:.4f} ± {hps_std:.4f}")

    # Diversity (select 40 random prompts and generate 25 images each)
    prompts = random.sample(env.base_model.prompts, 40)
    image_sets = []
    for prompt in tqdm(prompts):
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            samples, _, _, _, _, _, _, _, _ = env.sample(
                25,
                pbar=False,
                prompt=prompt,
                cfg_scale=args.cfg_scale,
            )
        images = []
        for i in range(len(samples)):
            images.append(to_pil_image(samples[i].to(dtype=torch.float)))

        image_sets.append(images)

    div = dreamsim_diversity(image_sets, device)
    print(f"DreamSim Diversity: {div:.4f}")

    stats = {
        "reward_mean": rewards.mean().item(),
        "reward_std": rewards.std().item(),
        "clip_mean": clip_mean,
        "clip_std": clip_std,
        "pick_mean": pick_mean,
        "pick_std": pick_std,
        "hps_mean": hps_mean,
        "hps_std": hps_std,
        "dreamsim_diversity": div,
    }
    with open(os.path.join(sample_dir, "stats.yaml"), "w") as f:
        yaml.dump(stats, f)


@torch.no_grad()
def clip_score(images: list[Image.Image], texts: list[str], device: torch.device) -> tuple[float, float]:
    assert len(images) == len(texts)

    # Load CLIP model
    model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k", device=device)
    model.eval()  # type: ignore
    tokenizer = open_clip.get_tokenizer("ViT-B-32")

    # Preprocess images/texts
    images = [preprocess(img).unsqueeze(0) for img in images]  # type: ignore
    tokenized_texts = tokenizer(texts).to(device)

    # Encode and normalize images/texts
    image_features = torch.cat([model.encode_image(img.to(device)) for img in images])  # type: ignore
    text_features = model.encode_text(tokenized_texts)  # type: ignore
    image_features /= image_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)

    # Compute CLIP scores
    clip_scores = torch.zeros(len(images))
    for i, (img_feat, txt_feat) in enumerate(zip(image_features, text_features)):
        clip_scores[i] = max(0, 100 * torch.dot(img_feat, txt_feat).item())

    return clip_scores.mean().item(), clip_scores.std().item()


@torch.no_grad()
def pick_score(images: list[Image.Image], texts: list[str], device: torch.device) -> tuple[float, float]:
    assert len(images) == len(texts)

    # Load models
    processor = AutoProcessor.from_pretrained("laion/CLIP-ViT-H-14-laion2B-s32B-b79K")
    model = AutoModel.from_pretrained("yuvalkirstain/PickScore_v1").eval().to(device)

    # Preprocess images/texts
    image_inputs = processor(
        images=images,
        padding=True,
        truncation=True,
        max_length=77,
        return_tensors="pt",
    ).to(device)
    text_inputs = processor(
        text=texts,
        padding=True,
        truncation=True,
        max_length=77,
        return_tensors="pt",
    ).to(device)

    # Encode and normalize images/texts
    image_features = torch.cat([model.get_image_features(**{k: v[i].unsqueeze(0) for k, v in image_inputs.items()}) for i in range(len(images))])
    text_features = torch.cat([model.get_text_features(**{k: v[i].unsqueeze(0) for k, v in text_inputs.items()}) for i in range(len(texts))])
    image_features /= image_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)

    # Compute Pick scores
    pick_scores = torch.zeros(len(images))
    for i, (img_feat, text_feat) in enumerate(zip(image_features, text_features)):
        pick_scores[i] = max(0, 100 * torch.dot(img_feat, text_feat).item())

    return pick_scores.mean().item(), pick_scores.std().item()


@torch.no_grad()
def human_preference_score(images: list[Image.Image], texts: list[str]) -> tuple[float, float]:
    assert len(images) == len(texts)

    scores = torch.zeros(len(images))
    for i, (img, txt) in enumerate(zip(images, texts)):
        scores[i] = max(0, 100 * float(hpsv2.score(img, txt, hps_version="v2.0")[0]))

    return scores.mean().item(), scores.std().item()


@torch.no_grad()
def dreamsim_diversity(image_sets: list[list[Image.Image]], device: torch.device) -> float:
    model, preprocess = dreamsim(pretrained=True, device=device)  # type: ignore

    diversity_sum = 0
    for imgs in image_sets:
        embs = [model.embed(preprocess(img).to(device)).cpu() for img in imgs]
        embs = torch.cat(embs)

        total_dist = 0
        for i in range(len(imgs)):
            for j in range(i+1, len(imgs)):
                total_dist += torch.square(embs[i] - embs[j]).sum().item()

        diversity_sum += (2 / (len(imgs) * (len(imgs)-1))) * total_dist

    return max(0, 100 * diversity_sum / len(image_sets))


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
    parser.add_argument("--sample_dir", type=str, required=True, help="Directory in --dir to save samples")
    parser.add_argument("--ckpt", type=str, default=None, help="Loads the weights in dir/checkpoints/<ckpt>")
    parser.add_argument("--num_samples", type=int, default=1_000, help="Number of samples to estimate the expectation.")
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size for sampling")
    parser.add_argument("--cfg_scale", type=float, default=0, help="Classifier-free guidance scale")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--prompt", type=str, default=None, help="Optional prompt that all samples will use.")
    args = parser.parse_args()
    main(args)
