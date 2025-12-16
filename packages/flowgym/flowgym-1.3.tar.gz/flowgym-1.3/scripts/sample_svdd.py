r"""Run value matching on specified environment and method.

Example usage:
```
python sample_svdd.py
```
"""

import argparse
import json
import math
import os
from itertools import pairwise
from typing import Any, Iterable

import torch
from torchvision.utils import save_image
from tqdm import tqdm
from vendi_score import vendi

import flowgym
from flowgym import Environment, FGTensor

from .eval_cifar import clip_features, fid


def main(args):
    """Evaluate SVDD."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    env = flowgym.make(
        args.base_model,
        args.reward,
        args.num_steps,
        device=device,
    )

    # Make dir for samples
    if args.sample_dir is not None:
        os.makedirs(args.sample_dir, exist_ok=True)

    rewards = torch.zeros(args.num_samples)
    image_tensors = []

    pbar = tqdm(batch_indices(args.num_samples, args.batch_size))
    for head, tail in pbar:
        samples, r, _, _ = sample_svdd_pm(env, tail - head, m=args.m, alpha=args.alpha, pbar=True, **(args.kwargs or {}))

        image_tensors.append(samples)

        for i in range(tail - head):
            if args.sample_dir is not None:
                save_image(samples[i].unsqueeze(0), os.path.join(args.sample_dir, f"{head+i:06d}.png"))

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
def sample_svdd_pm(
    env: Environment[FGTensor],
    n: int,
    m: int = 20,
    alpha: float = 0.0,
    pbar: bool = True,
    **kwargs: Any,
):
    x, kwargs = env.base_model.sample_p0(n, **kwargs)
    x, kwargs = env.base_model.preprocess(x, **kwargs)

    t = torch.linspace(2e-2, 1, env.discretization_steps + 1)
    iterator: Iterable[tuple[Any, Any]] = pairwise(t)
    if pbar:
        iterator = tqdm(iterator, total=env.discretization_steps)

    for t0, t1 in iterator:
        dt = t1 - t0
        t_curr = t0 * torch.ones(n, device=env.device)

        drift, _ = env.drift(x, t_curr, **kwargs)
        diffusion = env.diffusion(x, t_curr)

        # Sample M potential next steps
        epsilons = torch.randn(n, m, *x.shape[1:], device=env.device)
        values = torch.zeros(n, m)
        for j in range(m):
            # Generate random seed
            epsilon = epsilons[:, j]
            x_next = FGTensor(x + dt * drift + torch.sqrt(dt) * diffusion * epsilon)

            # Compute value v(x, t) = exp(r(x_final(x, t)))
            x_final = env.pred_final(x_next, t_curr + dt, **kwargs)
            x_final = env.base_model.postprocess(x_final)
            values[:, j] = env.reward(x_final, **kwargs)[0].cpu() / alpha

        if alpha > 0:
            # Take softmax-weighted combination
            weights = torch.softmax(values, dim=1)
            indices = torch.multinomial(weights, num_samples=1).squeeze(1)
        else:
            # Take maximizer
            indices = torch.argmax(values, dim=1)

        epsilon = epsilons[torch.arange(n), indices]

        x = FGTensor(x + dt * drift + torch.sqrt(dt) * diffusion * epsilon)

    x = env.base_model.postprocess(x)
    rewards, valids = env.reward(x, **kwargs)

    return x, rewards, valids, kwargs


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
    parser.add_argument("--base_model", type=str, required=True, help="Base model")
    parser.add_argument("--reward", type=str, required=True, help="Reward function")
    parser.add_argument("--num_steps", type=int, default=100, help="Number of timesteps to discretize the SDE")
    parser.add_argument("--num_samples", type=int, default=1_000, help="Number of samples to estimate the expectation.")
    parser.add_argument("--batch_size", type=int, default=128, help="Batch size for sampling")
    parser.add_argument("--m", type=int, default=20, help="Number of candidate samples for SVDD")
    parser.add_argument("--alpha", type=float, default=0.0, help="Alpha parameter for SVDD")
    parser.add_argument("--sample_dir", type=str, default=None, help="Directory to save samples")
    parser.add_argument(
        "--kwargs",
        type=json.loads,
        default=None,
        help="Kwargs to pass. Example: --kwargs '{\"cfg_scale\": 4.0}'",
    )
    args = parser.parse_args()
    print(
        f"""Evaluating SVDD on
    Base Model: {args.base_model}
    Reward: {args.reward}
    Num Steps: {args.num_steps}
    Num Samples: {args.num_samples}
    Batch Size: {args.batch_size}
    M: {args.m}
    Alpha: {args.alpha}
    """
    )
    main(args)
