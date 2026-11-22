"""Development evaluation of a candidate and numerical WLS on *paired* frames.

No output from this tool is a frozen paper test or confirmation result.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from .simulation import SimulationConfig, sample_batch
from .baseline import solve_mpr_wls


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


def main(argv=None):
    parser = argparse.ArgumentParser(description="Exploratory paired development comparison")
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--wls-samples", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20261231)
    parser.add_argument("--outlier-p", type=float, default=0.0)
    parser.add_argument("--output", default="runs/dev_eval.json")
    args = parser.parse_args(argv)
    if args.samples < 1 or args.wls_samples < 0:
        raise ValueError("invalid sample count")
    frames = sample_batch(np.random.default_rng(args.seed), args.samples,
                          SimulationConfig(outlier_probability=args.outlier_p))
    results = {"status": "development_only_not_confirmation",
               "seed": args.seed, "samples": args.samples,
               "outlier_probability": args.outlier_p,
               "methods": {}}
    if args.checkpoint:
        import torch
        from .neural import DynamicTDOAMPR
        ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
        model = DynamicTDOAMPR(ckpt["hidden"], ckpt["iterations"], ckpt["radial_limit"])
        model.load_state_dict(ckpt["model"])
        model.eval()
        with torch.no_grad():
            def t(key):
                return torch.as_tensor(frames[key], dtype=torch.float32)
            out = model(t("y"), t("stations"), t("qr"), t("qs"))
        results["methods"]["dynamic_neural_candidate"] = pairwise_risk(
            out["u"].numpy(), out["g"].numpy(), frames["u"], frames["g"])
        results["checkpoint_steps"] = int(ckpt["steps"])
    limit = min(args.wls_samples, args.samples)
    if limit:
        fitted = [solve_mpr_wls(frames["y"][i], frames["stations"][i],
                                frames["qr"][i], frames["qs"][i]) for i in range(limit)]
        stats = pairwise_risk(np.stack([v.u for v in fitted]),
                              [v.g for v in fitted], frames["u"][:limit], frames["g"][:limit])
        stats.update({"success_count": sum(v.success for v in fitted),
                      "label": "numerical_WLS_not_official_MLE_GTRS_SUM"})
        results["methods"]["numerical_wls"] = stats
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
