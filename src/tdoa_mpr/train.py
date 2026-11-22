"""Opt-in short development training; never a frozen paper experiment."""
import argparse
import json
from pathlib import Path
import numpy as np


def main(argv=None):
    import torch
    from .neural import DynamicTDOAMPR, joint_point_loss
    from .simulation import SimulationConfig, sample_batch

    parser = argparse.ArgumentParser(description="TDOA-MPR development training")
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--hidden", type=int, default=96)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--seed", type=int, default=20261123)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--outlier-p", type=float, default=0.0)
    parser.add_argument("--output", default="runs/dev.pt")
    args = parser.parse_args(argv)
    if args.steps < 1 or args.batch_size < 1:
        raise ValueError("steps and batch-size must be positive")
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    torch.set_num_threads(max(1, min(torch.get_num_threads(), 8)))
    config = SimulationConfig(outlier_probability=args.outlier_p)
    model = DynamicTDOAMPR(args.hidden, args.iterations).to(args.device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    history = []

    for step in range(args.steps):
        frame = sample_batch(rng, args.batch_size, config)
        def t(key):
            return torch.as_tensor(frame[key], dtype=torch.float32, device=args.device)
        model.train()
        result = model(t("y"), t("stations"), t("qr"), t("qs"))
        loss = joint_point_loss(result, t("u"), t("g"), t("stations"))
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=5.)
        optimizer.step()
        if step == 0 or (step + 1) % 25 == 0 or step + 1 == args.steps:
            record = {"step": step + 1, "training_batch_loss": float(loss.detach().cpu())}
            history.append(record)
            print(json.dumps(record))
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": model.state_dict(), "hidden": args.hidden,
                "iterations": args.iterations, "radial_limit": model.radial_limit,
                "seed": args.seed, "steps": args.steps,
                "simulation": config.to_dict(), "optimizer": optimizer.state_dict(),
                "loss_history": history, "status": "development_only"}, target)
    print("Saved development-only checkpoint:", target)


if __name__ == "__main__":
    main()
