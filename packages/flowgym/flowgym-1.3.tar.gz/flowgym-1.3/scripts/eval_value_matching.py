r"""Run value matching on specified environment and method.

Example usage:
```
python eval_value_matching.py --dir ./experiments/value_matching --ckpt last.ckpt
```
"""

import argparse
import math
import os

import torch
import yaml
from flowgym.methods.value_matching import ValuePolicy
from tqdm import tqdm

import flowgym

from .run_value_matching import get_value_network


def main(args):
    """Evaluate value matching."""
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

    if args.ckpt is not None:
        value_network = get_value_network(
            train_args["base_model"],
            train_args["depth"],
            train_args["width"],
            train_args["reward_scale"],
        ).to(device)
        value_network.load_state_dict(torch.load(os.path.join(args.dir, "checkpoints", args.ckpt), map_location=device))
        value_network.eval()
        control = ValuePolicy(value_network, env.memoryless_schedule)
        env.control_policy = control

    rewards = torch.zeros(args.num_samples)
    valids = torch.zeros(args.num_samples)

    pbar = tqdm(batch_indices(args.num_samples, args.batch_size))
    for head, tail in pbar:
        _, _, _, r, v, _, _, _ = env.sample(tail - head, pbar=False)
        rewards[head:tail] = r.squeeze().cpu()
        valids[head:tail] = v.float().squeeze().cpu()

        valid_rewards = rewards[:tail][valids[:tail].bool()]
        pbar.set_postfix(
            r_mean=rewards[:tail].mean().item(),
            r_std=rewards[:tail].std().item(),
            valid_r_mean=valid_rewards.mean().item(),
            valid_r_std=valid_rewards.std().item(),
            valids=valids[:tail].mean().item(),
        )

    print("Reward mean:", rewards.mean().item())
    print("Reward std:", rewards.std().item())
    print("Valid reward mean:", rewards[valids.bool()].mean().item())
    print("Valid reward std:", rewards[valids.bool()].std().item())
    print("Validity:", valids.mean().item())

    ckpt = args.ckpt.split(".")[0] if args.ckpt is not None else "base"
    torch.save(rewards, os.path.join(args.dir, f"{ckpt}_rewards.pt"))
    torch.save(valids, os.path.join(args.dir, f"{ckpt}_valids.pt"))


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
    parser.add_argument("--ckpt", type=str, default=None, help="Loads the weights in dir/checkpoints/<ckpt>")
    parser.add_argument("--num_steps", type=int, default=100, help="Number of timesteps to discretize the SDE")
    parser.add_argument("--num_samples", type=int, default=10_000, help="Number of samples to estimate the expectation.")
    parser.add_argument("--batch_size", type=int, default=128, help="Batch size for sampling")
    args = parser.parse_args()
    main(args)
