"""Score paired Sun 2019 figure data from experiments/run_cisp_sweep.m."""
import hashlib

import numpy as np
from scipy.io import loadmat


def _directions(angles):
    az, el = angles[..., 0], angles[..., 1]
    return np.stack([np.cos(az)*np.cos(el), np.sin(az)*np.cos(el), np.sin(el)], axis=-1)


def _metrics(state, pos, angles, ranges):
    # Axes are frame, sweep point, coordinate. Retain every frame in a mean.
    state = np.where(np.isreal(state) & np.isfinite(state), state.real, np.nan)
    pos = np.where(np.isreal(pos) & np.isfinite(pos), pos.real, np.nan)
    a, g = state[..., :2], state[..., 2]
    true_u = _directions(angles)
    u = _directions(a)
    geodesic = np.arctan2(np.linalg.norm(np.cross(u, true_u), axis=-1), u @ true_u)
    dp = pos - ranges[:, None]*true_u
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        values = {
            "angle_mse_rad2": np.mean(np.sum((a-angles)**2, axis=-1), axis=0),
            "g_mse_mminus2": np.mean((g-1/ranges)**2, axis=0),
            "position_mse_m2": np.mean(np.sum(dp**2, axis=-1), axis=0),
            "range_mse_m2": np.mean((1/g-ranges)**2, axis=0),
            # Example.m averages the magnitudes of the two angle coordinates.
            "folded_angle_bias_rad": np.linalg.norm(np.mean(np.abs(a), axis=0)-angles, axis=-1),
            "g_bias_mminus1": np.abs(np.mean(g, axis=0)-1/ranges),
            "position_bias_m": np.linalg.norm(np.mean(dp, axis=0), axis=-1),
            "spherical_mse_rad2": np.mean(geodesic**2, axis=0),
        }
    result = {key: [float(v) if np.isfinite(v) else None for v in series]
              for key, series in values.items()}
    result["valid_mpr"] = np.isfinite(state).all(axis=-1).sum(axis=0).tolist()
    result["negative_g"] = (g < 0).sum(axis=0).tolist()
    return result


def evaluate_sweep(path, predict=None):
    """Evaluate the saved six range differences per frame, with reference 0."""
    data = loadmat(path, simplify_cells=True)
    ranges = data["range_m"]
    angles = data["angles"]
    names = data["method_names"].tolist()
    device_iot = ["SCO", "SUM", "GTRS"]
    if names not in (device_iot, device_iot + ["Chan-Ho"]):
        raise ValueError(f"unexpected sweep method columns: {names}")
    methods = {}
    for i, name in enumerate(names):
        methods[name] = _metrics(data["mpr"][:,i].transpose(1,2,0),
                                 data["position"][:,i].transpose(1,2,0), angles, ranges)
        for field in ("warnings", "errors"):
            # Empty MATLAB cells load as empty ndarrays. Nonempty cells hold text.
            methods[name][field] = [sum(isinstance(v, str) and bool(v) for v in col)
                                    for col in data[field][i].T]
    if predict is not None:
        count = data["ensembles"]
        stations = np.repeat(data["stations"].T[None], count, axis=0)
        qs = np.repeat(data["Qs"][None], count, axis=0)
        states, positions = [], []
        for k in range(len(ranges)):
            qr = np.repeat(data["Qr"][None,:,:,k], count, axis=0)
            u, g = predict(data["y"][:,:,k].T, stations, qr, qs)
            u, g = np.asarray(u, dtype=float), np.asarray(g, dtype=float)
            norm = np.linalg.norm(u, axis=-1, keepdims=True)
            with np.errstate(invalid="ignore", divide="ignore"):
                u = u / norm
                positions.append(u / g[:, None])
            states.append(np.column_stack([np.arctan2(u[:,1], u[:,0]),
                                           np.arctan2(u[:,2], np.hypot(u[:,0], u[:,1])), g]))
        methods["Neural"] = _metrics(np.stack(states, axis=1), np.stack(positions, axis=1),
                                     angles, ranges)

    provenance = {"device_iot_zip_sha256": data["device_iot_zip_sha256"]}
    if "Chan-Ho" in names:
        provenance["chan_ho_zip_sha256"] = data["chan_ho_zip_sha256"]
    return {"status": "development_only_not_confirmation", "sweep": data["sweep"],
            "input_mat": str(path), "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            **provenance,
            "frames_per_point": data["ensembles"], "original_frames_per_point": data["official_ensembles"],
            "range_km": (ranges/1000).tolist(), "tdoa_variance_db": data["variance_db"].tolist(),
            "matlab_release": data["matlab_release"], "methods": methods,
            "crlb": data["crlb"].tolist(), "bias_theory_2019": data["bias_2019"].tolist()}


def plot_sweep(result, folder):
    """Draw the Sun 2019 panels in the paired layout of the DMPR paper demo."""
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    noise = result["sweep"] == "noise"
    x = result["tdoa_variance_db"] if noise else result["range_km"]
    xlabel = (r"$10\log_{10}(\sigma_n^2/\mathrm{m}^2)$" if noise
              else r"$\mathrm{Range}\;(\mathrm{km})$")
    # MATLAB plotConfigDefault.mat slots 1–3, 4 (neural), 6 (Cartesian TSWLS), 7 (bound).
    styles = {"SCO": ("#0072bd", "o"), "SUM": ("#d95319", "^"),
              "GTRS": ("#edb120", (6, 2, 0)), "Chan-Ho": ("#4dbeee", "+"),
              "Neural": ("#7e2f8e", "s")}
    # Each row binds a metric to its own CRLB or its 2019 theoretical bias.
    mse = [("angle_mse_rad2", r"\mathrm{MSE}(\theta,\phi)/\mathrm{rad}^2", 0),
           ("g_mse_mminus2", r"\mathrm{MSE}(g)/\mathrm{m}^{-2}", 1),
           ("position_mse_m2", r"\mathrm{MSE}(\mathbf{p})/\mathrm{m}^2", 2),
           ("range_mse_m2", r"\mathrm{MSE}(r)/\mathrm{m}^2", 3)]
    bias = [("folded_angle_bias_rad", r"\mathrm{Bias}_{\mathrm{fold}}(\theta,\phi)/\mathrm{rad}", 0),
            ("g_bias_mminus1", r"|\mathrm{Bias}(g)|/\mathrm{m}^{-1}", 1),
            ("position_bias_m", r"\Vert\mathrm{Bias}(\mathbf{p})\Vert/\mathrm{m}", 2)]
    figures = [("mpr_mse", 10, mse[:2]), ("mpr_bias", 20, bias[:2])]
    if noise:
        figures.extend([("position_range_mse", 10, mse[2:]), ("position_bias", 20, bias[2:])])
    rc = {"font.family": "sans-serif", "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
          "mathtext.fontset": "cm", "pdf.fonttype": 42, "axes.linewidth": 0.6,
          "xtick.labelsize": 10, "ytick.labelsize": 10, "axes.labelsize": 13}
    folder.mkdir(parents=True, exist_ok=True)
    with mpl.rc_context(rc), np.errstate(divide="ignore", invalid="ignore"):
        for stem, factor, panels in figures:
            n = len(panels)
            fig, axes = plt.subplots(n, 1, figsize=(5.6, 6 if n == 2 else 3.2),
                                     squeeze=False, layout="constrained")
            for ax, (metric, formula, j) in zip(axes[:, 0], panels):
                for name, values in result["methods"].items():
                    color, marker = styles[name]
                    db = factor * np.log10(np.asarray(values[metric], dtype=float))
                    ax.plot(x, db, color=color, marker=marker, markersize=6, markerfacecolor="none",
                            markeredgewidth=1.5, linestyle="none", zorder=3,
                            label="Chan–Ho (Cartesian)" if name == "Chan-Ho" else name)
                if factor == 10:
                    ax.plot(x, 10*np.log10(result["crlb"][j]), color="#a2142f", lw=1.5, label="CRLB")
                else:
                    for theory, name, line in zip(result["bias_theory_2019"][j], ("SUM", "GTRS"), ("--", "-.")):
                        ax.plot(x, 20*np.log10(theory), linestyle=line, color=styles[name][0],
                                lw=1.5, label=f"{name} theory (2019)")
                ax.set(xlabel=xlabel, ylabel=rf"${factor}\log_{{10}}\!\left({formula}\right)$")
                if noise:
                    ax.set_xticks(x)
                else:
                    ax.set_xticks([v for v in x if v in (x[0], x[-1]) or v % 100 == 0])
                ax.margins(x=0.018, y=0.08)
                if not noise and factor == 20:
                    lo, hi = ax.get_ylim()
                    ax.set_ylim(lo, hi + 0.13*(hi-lo))
                ax.grid(color="#d9d9d9", linewidth=0.5)
                ax.tick_params(direction="in", top=True, right=True, length=3, width=0.6)
                legend = ax.legend(loc="upper left", ncols=1 if factor == 10 else 2, fontsize=9,
                                   fancybox=False, framealpha=1, edgecolor="#606060",
                                   handlelength=1.8, handletextpad=0.5, borderpad=0.35, labelspacing=0.2)
                legend.get_frame().set_linewidth(0.6)
            if result["frames_per_point"] != result["original_frames_per_point"]:
                fig.supxlabel(f"Development · {result['frames_per_point']} frames per point",
                              fontsize=8, color="#555555")
            for ext in ("pdf", "png"):
                fig.savefig(folder / f"{stem}_{result['sweep']}.{ext}", dpi=180)
            plt.close(fig)
