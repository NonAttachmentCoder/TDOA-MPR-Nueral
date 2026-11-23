"""Score the DeviceIoT and Cartesian methods and an optional network on saved sweeps."""
import argparse
import json
from pathlib import Path
import numpy as np
from .simulation import LegacyEightReceiverConfig, SimulationConfig, sample_batch


def pairwise_risk(estimate_u, estimate_g, true_u, true_g):
    uhat = np.asarray(estimate_u, dtype=np.float64)
    ghat = np.asarray(estimate_g, dtype=np.float64).reshape(-1)
    u = np.asarray(true_u, dtype=np.float64)
    g = np.asarray(true_g, dtype=np.float64).reshape(-1)
    ok = np.isfinite(uhat).all(axis=-1) & np.isfinite(ghat)
    norms = np.linalg.norm(uhat, axis=-1)
    ok &= norms > 1e-10
    if not np.any(ok):
        return {"valid": 0, "total": len(g), "direction_mse_rad2": None,
                "inverse_range_mse_mminus2": None}
    inner = np.clip(np.sum((uhat[ok] / norms[ok, None]) * u[ok], axis=-1), -1., 1.)
    theta2 = np.arccos(inner)**2
    dg2 = (ghat[ok] - g[ok])**2
    return {"valid": int(ok.sum()), "total": len(g),
            "direction_mse_rad2": float(np.mean(theta2)),
            "inverse_range_mse_mminus2": float(np.mean(dg2)),
            "negative_g_count": int((ghat[ok] < 0).sum())}


def _load_model(path):
    import torch
    from .neural import DynamicTDOAMPR
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    # The original checkpoint format always used eight stations.
    receivers = ckpt.get("simulation", {}).get("n_receivers", 8)
    model = DynamicTDOAMPR(ckpt["hidden"], ckpt["iterations"], ckpt["radial_limit"],
                           use_physical_query=ckpt.get("use_physical_query", True),
                           use_full_qr=ckpt.get("use_full_qr", True), n_receivers=receivers)
    model.load_state_dict(ckpt["model"])
    model.eval()

    @torch.no_grad()
    def predict(y, stations, qr, qs):
        out = model(*(torch.as_tensor(a, dtype=torch.float32) for a in (y, stations, qr, qs)))
        return out["u"].numpy(), out["g"].numpy()

    return predict, receivers, ckpt["steps"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep", type=Path, help="MAT file written by run_cisp_sweep")
    parser.add_argument("--figures", type=Path, help="directory for the source-style sweep panels")
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--samples", type=int, help="checkpoint-only smoke frames (default 64)")
    parser.add_argument("--seed", type=int, help="checkpoint-only smoke seed (default 20261231)")
    parser.add_argument("--outlier-p", type=float, help="checkpoint-only outlier probability (default 0)")
    parser.add_argument("--output", default="runs/dev_eval.json")
    args = parser.parse_args(argv)
    if not args.sweep and not args.checkpoint:
        parser.error("supply --sweep for the classical baselines or --checkpoint for a network smoke check")
    if args.figures and not args.sweep:
        parser.error("--figures requires --sweep")
    if args.sweep and any(v is not None for v in (args.samples, args.seed, args.outlier_p)):
        parser.error("--sweep uses the draws saved in the MAT file; sampling options apply only to smoke frames")
    predict, receivers, steps = _load_model(args.checkpoint) if args.checkpoint else (None, 7, None)
    if args.sweep:
        from .sweeps import evaluate_sweep, plot_sweep
        if receivers != 7:
            parser.error("the published geometry requires a seven-receiver checkpoint")
        results = evaluate_sweep(args.sweep, predict)
        if args.figures:
            plot_sweep(results, args.figures)
    else:
        config = LegacyEightReceiverConfig if receivers == 8 else SimulationConfig
        samples = 64 if args.samples is None else args.samples
        seed = 20261231 if args.seed is None else args.seed
        outlier_p = 0.0 if args.outlier_p is None else args.outlier_p
        frames = sample_batch(np.random.default_rng(seed), samples, config(outlier_probability=outlier_p))
        u, g = predict(*(frames[k] for k in ("y", "stations", "qr", "qs")))
        results = {"status": "development_only_not_confirmation", "seed": seed,
                   "samples": samples, "outlier_probability": outlier_p,
                   "methods": {"dynamic_neural_candidate": pairwise_risk(u, g, frames["u"], frames["g"])}}
    if args.checkpoint:
        results.update(checkpoint=str(args.checkpoint), checkpoint_steps=int(steps))
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(results, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Saved {', '.join(results['methods'])} results to {target}")


if __name__ == "__main__":
    main()
