r"""Run value matching on specified environment and method.

Example usage:
```
python run_value_matching.py \
    --dir ./experiments/value_matching \
    --base_model molecules/flowmol \
    --reward molecules/dipole_moment
```
"""

import argparse
import json
import logging
import os

import torch
import yaml
from flowgym.methods.ddpo import ddpo

import flowgym


def main(args):
    """Run DDPO."""
    os.makedirs(args.dir, exist_ok=True)

    with open(os.path.join(args.dir, "args.yaml"), "w") as f:
        yaml.dump(vars(args), f)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(args.dir, "log.txt")),
        ]
    )
    logging.info("starting run")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"device: {device}")

    env = flowgym.make(
        args.base_model,
        args.reward,
        args.num_steps,
        device=device,
        base_model_kwargs=args.base_model_kwargs,
        reward_kwargs=args.reward_kwargs,
    )
    env.base_model = env.base_model.to(dtype=torch.bfloat16)

    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        ddpo(
            env=env,
            num_iterations=args.num_iters,
            trajectories_per_iteration=args.traj_per_iter,
            batch_size=args.batch_size,
            lr=args.lr,
            log_every=args.log_every,
            exp_dir=args.dir,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run value matching on a specified environment and method",
    )
    parser.add_argument("--dir", type=str, required=True, help="Experiment directory")
    parser.add_argument("--base_model", type=str, required=True, help="The base model to use")
    parser.add_argument("--reward", type=str, required=True, help="The reward function to use")
    parser.add_argument("--num_steps", type=int, default=100, help="Number of discretization steps")
    parser.add_argument("--num_iters", type=int, default=500, help="Number of training iterations")
    parser.add_argument("--traj_per_iter", type=int, default=256, help="Number of trajectories per iteration")
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-5, help="Learning rate")
    parser.add_argument("--log_every", type=int, default=None, help="Log every n steps")
    parser.add_argument(
        "--base_model_kwargs",
        type=json.loads,
        default=None,
        help="JSON string of keyword arguments for the base model. "
             "Example: --base_model_kwargs '{\"key1\": \"value1\", \"key2\": 123}'"
    )
    parser.add_argument(
        "--reward_kwargs",
        type=json.loads,
        default=None,
        help="JSON string of keyword arguments for the reward function. "
             "Example: --reward_kwargs '{\"relax\": true}'"
    )
    args = parser.parse_args()
    main(args)
