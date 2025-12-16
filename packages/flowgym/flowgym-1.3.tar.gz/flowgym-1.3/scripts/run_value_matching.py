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
import warnings
import os

import torch
import yaml
from torch import nn

import flowgym
from value_matching import value_matching

from .architectures import CNN, GNN, MLP


def main(args):
    """Run value matching."""
    warnings.filterwarnings("ignore", message=".*CLIP.*77 tokens.*")

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

    value_network = get_value_network(args.base_model, args.reward, args.depth, args.width, args.reward_scale)

    # Load 
    state_dict = torch.load("/cluster/scratch/cjense/msc-thesis/sd1.5/vm/image_reward_500_from_ckpt_corrected/checkpoints/last.pt")
    value_network.load_state_dict(state_dict)

    value_network = value_network.to(device, dtype=torch.bfloat16)
    logging.info(f"value network parameters: {sum(p.numel() for p in value_network.parameters()):,}")

    env = flowgym.make(
        args.base_model,
        args.reward,
        args.num_steps,
        args.reward_scale,
        device=device,
        base_model_kwargs=args.base_model_kwargs,
        reward_kwargs=args.reward_kwargs,
    )
    env.base_model = env.base_model.to(dtype=torch.bfloat16)

    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
        value_matching(
            value_network=value_network,
            env=env,
            batch_size=args.batch_size,
            num_iterations=args.num_iters,
            lr=args.lr,
            log_every=args.log_every,
            exp_dir=args.dir,
            kwargs=args.kwargs,
        )


def get_value_network(
    base_model: str,
    reward: str,
    depth: int = 1,
    width: int = 64,
    reward_scale: int = 1,
) -> nn.Module:
    """Get the appropriate value network architecture for the base model.

    Parameters
    ----------
    base_model : str
        Base model identifier in format 'domain/task', where domain is one of
        {'molecules', 'images', '1d'} and task specifies the specific environment.

    reward : str
        Reward identifier in format 'domain/reward'.

    depth : int
        Depth parameter for the architecture. For CNNs, it is the number of blocks per stage.

    width : int
        Width parameter for the architecture. For CNNs, it is the base number of channels.

    reward_scale : int
        Reward scale parameter.

    Returns
    -------
    model : nn.Module
        Initialized value network architecture appropriate for the domain.

    Raises
    ------
    ValueError
        If the domain or task is not recognized.
    """
    domain, task = base_model.split("/")
    if domain == "molecules":
        if "geom" in task:
            return GNN(19, 5, scale=reward_scale)

        if "qm9" in task:
            target_index = None
            target_mean = 0.0
            target_std = 1.0
            if "target_dipole_moment" in reward:
                target_index = "dipole_moment_target"
                target_mean = 2.6822
                target_std = 1.4974

            return GNN(14, 5,
                target_index=target_index,
                target_mean=target_mean,
                target_std=target_std,
                scale=reward_scale,
            )

        raise ValueError("Unknown molecular task: {task}")

    if domain == "images":
        if task == "cifar":
            return CNN(3, base_ch=width, num_blocks_per_stage=depth, scale=reward_scale)

        if task == "sd" or task == "sd1.5":
            return CNN(4, base_ch=width, num_blocks_per_stage=depth, scale=reward_scale, text_cond=True)

        if task == "dit":
            return CNN(4, base_ch=width, num_blocks_per_stage=depth, scale=reward_scale)

        raise ValueError(f"Unknown image task: {task}")

    if domain == "1d":
        return MLP(1, 1)

    raise ValueError(f"Unknown base model domain: {domain}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run value matching on a specified environment and method",
    )
    parser.add_argument("--dir", type=str, required=True, help="Experiment directory")
    parser.add_argument("--base_model", type=str, required=True, help="The base model to use")
    parser.add_argument("--depth", type=int, default=1, help="Number of blocks per stage of the CNN (total 3 stages).")
    parser.add_argument("--width", type=int, default=64, help="Base number of channels in the CNN.")
    parser.add_argument("--reward", type=str, required=True, help="The reward function to use")
    parser.add_argument("--reward_scale", type=float, default=100, help="Reward scaling factor")
    parser.add_argument("--num_steps", type=int, default=100, help="Number of discretization steps")
    parser.add_argument("--num_iters", type=int, default=1000, help="Number of training iterations")
    parser.add_argument("--batch_size", type=int, default=128, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
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
    parser.add_argument(
        "--kwargs",
        type=json.loads,
        default=None,
        help="JSON string of keyword arguments for the value network. "
             "Example: --kwargs '{\"cfg_scale\": 4.0}'"
    )
    args = parser.parse_args()
    main(args)
