"""Bounded development checks for the initial review; no training or test bank.

Run from the repository root with .venv/bin/python. All generated randomness
is public development evidence. MATLAB fixtures go to the ignored runs/ tree.
"""
from pathlib import Path
import hashlib
import json
import platform
import subprocess

import numpy as np
import scipy
from scipy.io import savemat
import torch

from tdoa_mpr.physics import range_differences, mpr_jacobians, tangent_basis, local_information
from tdoa_mpr.covariance import differencing_matrix, effective_covariance
from tdoa_mpr.simulation import sample_batch, sample_frame, LegacyEightReceiverConfig
from tdoa_mpr.neural import DynamicTDOAMPR, joint_point_loss, torch_range_differences
from tdoa_mpr.baseline import solve_mpr_wls


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "evidence"
SEED = 2026112301


def relative(a, b):
    return float(np.linalg.norm(a-b) / max(np.linalg.norm(b), 1e-30))


def main():
    torch.set_num_threads(2)
    rng = np.random.default_rng(SEED)
    s = rng.normal(size=(8, 3)) * 25
    s[0] = [9, -6, 4]
    u = np.array([.7, -.2, .5]); u /= np.linalg.norm(u)
    E = tangent_basis(u)
    result = {"role": "development_diagnostics_not_performance_confirmation", "seed": SEED,
              "environment": {"python": platform.python_version(), "numpy": np.__version__,
                              "scipy": scipy.__version__, "torch": torch.__version__,
                              "platform": platform.platform()},
              "source_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()}
    result["working_source_sha256"] = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [*sorted((ROOT/"src/tdoa_mpr").glob("*.py")), Path(__file__).resolve()]}
    # Cartesian distances, independent analytic station derivatives, and FD.
    checks = []
    for g in (0., 1e-13, 1/80000., 1/300., 1/60., -1/300.):
        j = mpr_jacobians(u, g, s)
        eps_g = 1e-8
        dg_fd = (range_differences(u, g+eps_g, s)-range_differences(u, g-eps_g, s))/(2*eps_g)
        du_fd = np.column_stack([(range_differences(u+1e-7*a, g, s)-range_differences(u-1e-7*a, g, s))/2e-7 for a in np.eye(3)])
        ds_fd = np.column_stack([(range_differences(u, g, s+1e-5*a.reshape(8, 3))-range_differences(u, g, s-1e-5*a.reshape(8, 3)))/2e-5 for a in np.eye(24)])
        b = u-g*s; b /= np.linalg.norm(b, axis=1, keepdims=True)
        js_independent = np.zeros((7, 24))
        for k in range(7):
            js_independent[k, :3] = b[0]
            js_independent[k, 3*(k+1):3*(k+2)] = -b[k+1]
        row = {"g": g, "du_fd_max_abs": float(np.max(abs(j.du-du_fd))),
               "dg_fd_relative": relative(j.dg, dg_fd), "ds_fd_max_abs": float(np.max(abs(j.ds-ds_fd))),
               "ds_analytic_max_abs": float(np.max(abs(j.ds-js_independent)))}
        if g > 1e-10:
            d = np.linalg.norm(u/g-s, axis=1)
            row["cartesian_forward_max_abs_m"] = float(np.max(abs(range_differences(u, g, s)-(d[1:]-d[0]))))
        checks.append(row)
        assert row["du_fd_max_abs"] < 2e-6 and row["dg_fd_relative"] < 1e-7
        assert row["ds_fd_max_abs"] < 1e-8 and row["ds_analytic_max_abs"] < 1e-12
    result["derivatives"] = checks
    P = np.eye(3)-np.outer(u, u)
    curved = .5*(np.sum((s[1:]@P)**2, axis=1)-np.sum((s[0]@P)**2))
    result["g_zero_curvature_max_abs"] = float(np.max(abs(mpr_jacobians(u, 0, s).dg-curved)))

    # Reference changes preserve the whole quadratic likelihood and information.
    A = rng.normal(size=(8, 8)); qtoa = (A@A.T+np.eye(8))*.03
    D = differencing_matrix(8); qr = D@qtoa@D.T
    B = rng.normal(size=(24, 24)); qs = .001*(B@B.T+np.eye(24))
    g = 1/300.
    j = mpr_jacobians(u, g, s)
    H = np.column_stack((j.du@E, j.dg))
    C = effective_covariance(qr, j.ds, qs)
    F = H.T@np.linalg.solve(C, H)
    noise = rng.normal(size=7)
    refs = []
    for ref in (1, 4, 7):
        Dr = differencing_matrix(ref=ref)
        T = Dr@D.T@np.linalg.inv(D@D.T)
        jr = mpr_jacobians(u, g, s, ref)
        Hr = np.column_stack((jr.du@E, jr.dg))
        Cr = effective_covariance(T@qr@T.T, jr.ds, qs)
        refs.append({"ref": ref, "forward_max_abs": float(np.max(abs(range_differences(u, g, s, ref)-T@range_differences(u, g, s)))),
                     "information_relative": relative(Hr.T@np.linalg.solve(Cr, Hr), F),
                     "quadratic_error": float(abs((T@noise)@np.linalg.solve(Cr, T@noise)-noise@np.linalg.solve(C, noise)))})
    result["reference_invariance"] = refs

    # Exact joint Gaussian nuisance FIM (not a marginalized likelihood).
    QinvH = np.linalg.solve(qr, H); QinvJ = np.linalg.solve(qr, j.ds)
    cross = H.T@QinvJ
    schur = H.T@QinvH-cross@np.linalg.solve(j.ds.T@QinvJ+np.linalg.inv(qs), cross.T)
    result["joint_gaussian_nuisance_schur_relative"] = relative(schur, F)
    assert result["joint_gaussian_nuisance_schur_relative"] < 1e-10

    # Fixed-coordinate change, signed continuation, and unit conversion.
    a = np.array([13., -9., 5.])
    translations = []
    for gg in (0., 1/300., -1/300.):
        v = u-gg*a; norm = np.linalg.norm(v)
        err = range_differences(v/norm, gg/norm, s-a)-range_differences(u, gg, s)
        translations.append({"g": gg, "max_abs_m": float(np.max(abs(err)))})
    result["origin_translation"] = translations
    result["km_scaling_max_abs"] = float(np.max(abs(range_differences(u, g*1000, s/1000)*1000-range_differences(u, g, s))))
    meter_bound = local_information(u, g, s, qr)
    km_bound = local_information(u, g*1000, s/1000, qr/1e6)
    result["condition_depends_on_units"] = {"m": meter_bound.condition, "km": km_bound.condition,
                                            "direction_bound_relative": abs(meter_bound.direction_trace/km_bound.direction_trace-1)}
    line = np.zeros((8, 3)); line[:, 0] = np.arange(8)*10.
    result["collinear_bound_valid"] = local_information(u, g, line, np.eye(7)).valid

    # Nonzero curvature need not carry radial information after fitting direction.
    angles = np.arange(8)*2*np.pi/8
    cylinder = np.column_stack((20*(1-np.cos(angles)), 20*np.sin(angles),
                                20*np.array([0., -.7, .8, -.3, .4, -.5, .2, .9])))
    control = s-s[0]
    aperture = lambda ss: np.sqrt(np.mean(np.sum((ss-ss.mean(0))**2, axis=1)))
    control *= aperture(cylinder)/aperture(control)
    radial_checks = []
    for name, ss in (("cylinder", cylinder), ("same_aperture_control", control)):
        jj = mpr_jacobians(np.array([0., 0., 1.]), 0., ss)
        angular = jj.du[:, :2]
        b = jj.dg
        radial_residual = b-angular@np.linalg.lstsq(angular, b, rcond=None)[0]
        radial_checks.append({"geometry": name, "aperture_m": float(aperture(ss)),
                              "station_rank": int(np.linalg.matrix_rank(ss)),
                              "raw_radial_information_identity_Q": float(b@b),
                              "profile_radial_information_identity_Q": float(radial_residual@radial_residual)})
    result["curvature_vs_identifiability"] = radial_checks

    # A small fixed-geometry MC checks covariance, not estimator performance.
    n = 4096
    z = rng.normal(size=(n, 24))
    pos_checks = []
    for sigma in (.02, .2, 2.):
        errors = z*sigma
        exact = np.stack([range_differences(u, g, s+ee.reshape(8, 3))-range_differences(u, g, s) for ee in errors])
        linear = errors@j.ds.T
        predicted = j.ds@(np.eye(24)*sigma**2)@j.ds.T
        pos_checks.append({"sigma_m": sigma, "draws": n,
                           "empirical_covariance_relative": relative(np.cov(exact, rowvar=False), predicted),
                           "linearization_rms_fraction": float(np.linalg.norm(exact-linear)/np.linalg.norm(linear)),
                           "mean_residual_norm_m": float(np.linalg.norm(exact.mean(0)))})
    result["position_propagation"] = pos_checks
    frames = sample_batch(rng, 2048, LegacyEightReceiverConfig())
    white_r = np.stack([np.linalg.solve(np.linalg.cholesky(q), yy-h) for q, yy, h in zip(frames["qr"], frames["y"], frames["clean_y"])])
    white_s = (frames["stations"]-frames["s_true"]).reshape(-1, 24)/np.sqrt(np.diagonal(frames["qs"], axis1=1, axis2=2))
    result["generator_gaussian"] = {"draws": 2048, "white_r_mean_max_abs": float(abs(white_r.mean(0)).max()),
        "white_r_cov_identity_relative": relative(np.cov(white_r, rowvar=False), np.eye(7)),
        "white_s_variance_minmax": [float(white_s.var(0).min()), float(white_s.var(0).max())],
        "cross_covariance_max_abs": float(abs((white_r-white_r.mean(0)).T@(white_s-white_s.mean(0))/2048).max()),
        "reference_true_max_abs": float(abs(frames["s_true"][:, 0]).max()),
        "qs_offdiagonal_max_abs": float(abs(frames["qs"]*(1-np.eye(24))).max()),
        "reference_error_identity_max_abs": float(abs(frames["y"]-frames["clean_y"]-(frames["arrival_error"][:, 1:]-frames["arrival_error"][:, :1])).max())}
    # One receiver-0 bias shifts every TDOA with the same negative sign.
    ee = np.zeros(8); ee[0] = 5.
    result["reference_positive_bias_tdoa_m"] = (D@ee).tolist()
    result["all_receivers_equal_bias_cancels_max_abs"] = float(abs(D@np.full(8, 5.)).max())
    clean_frame = sample_frame(np.random.default_rng(SEED+1), LegacyEightReceiverConfig())
    biased_frame = sample_frame(np.random.default_rng(SEED+1),
                                LegacyEightReceiverConfig(positive_delay_bias_probability=1.))
    result["generator_equal_positive_bias"] = {
        "arrival_bias_error_max_abs": float(abs(biased_frame["arrival_error"]-clean_frame["arrival_error"]-5.).max()),
        "tdoa_difference_max_abs": float(abs(biased_frame["y"]-clean_frame["y"]).max())}
    inflated = sample_batch(np.random.default_rng(SEED+2), 512, LegacyEightReceiverConfig(outlier_probability=1.))
    toa_variances = np.column_stack((inflated["qr"][:, 0, 1],
                                    np.diagonal(inflated["qr"], axis1=1, axis2=2)-inflated["qr"][:, 0, 1, None]))
    normalized = inflated["arrival_error"]/np.sqrt(toa_variances)
    result["generator_variance_inflation"] = {"frames": 512, "expected_variance": 64.,
                                               "pooled_empirical_variance": float(normalized.var())}

    # Frozen random network: verify feature paths and gradients, never optimize.
    torch.manual_seed(SEED)
    model = DynamicTDOAMPR(n_receivers=8).double()
    inputs = [torch.from_numpy(frames[key][:8]) for key in ("y", "stations", "qr", "qs")]
    outputs = model(*inputs)
    loss = joint_point_loss(outputs, torch.from_numpy(frames["u"][:8]), torch.from_numpy(frames["g"][:8]), inputs[1])
    loss.backward()
    start = 2*model.hidden+49+7
    grad_qs = model.global_encoder[0].weight.grad[:, start:start+576].reshape(model.hidden, 24, 24)
    offdiag = ~torch.eye(24, dtype=torch.bool)
    result["neural_paths"] = {"parameters": sum(p.numel() for p in model.parameters()),
        "qs_offdiagonal_columns": 552, "qs_offdiagonal_weight_gradient_max_abs": float(grad_qs[:, offdiag].abs().max()),
        "qs_diagonal_weight_gradient_max_abs": float(grad_qs.diagonal(dim1=-2, dim2=-1).abs().max()),
        "all_gradients_finite": all(p.grad is None or torch.isfinite(p.grad).all().item() for p in model.parameters()),
        "untrained_outputs_are_not_accuracy_evidence": True}
    autograd = []
    for gg in (0., 1/300., -1/300.):
        ut = torch.tensor(u, requires_grad=True, dtype=torch.float64)
        gt = torch.tensor(gg, requires_grad=True, dtype=torch.float64)
        st = torch.tensor(s, requires_grad=True, dtype=torch.float64)
        Ju, Jg, Js = torch.autograd.functional.jacobian(
            lambda uu, ggg, ss: torch_range_differences(torch.nn.functional.normalize(uu, dim=0)[None], ggg[None], ss[None])[0],
            (ut, gt, st))
        jj = mpr_jacobians(u, gg, s)
        autograd.append({"g": gg, "du_max_abs": float(abs(Ju.numpy()-jj.du).max()),
                         "dg_max_abs": float(abs(Jg.numpy()-jj.dg).max()), "ds_max_abs": float(abs(Js.numpy().reshape(7, 24)-jj.ds).max())})
    result["independent_torch_autograd"] = autograd

    # Development fixtures, including coordinate translation and hemisphere.
    s0 = s-s[0]
    cases = []
    for name, el, rr in [("positive", .4, 300.), ("negative", -.4, 300.),
                         ("equator", 0., 300.), ("near", .4, 60.), ("far", .4, 80000.),
                         ("plane_wave", .4, np.inf), ("signed_diagnostic", .4, -300.)]:
        direction = np.array([np.cos(.7)*np.cos(el), np.sin(.7)*np.cos(el), np.sin(el)])
        cases.append({"name": name, "stations": s0, "u": direction, "g": 1/rr,
                      "y": range_differences(direction, 1/rr, s0), "qr": qr})
    base = cases[0]
    shifted_s = s0+a; p = base["u"]/base["g"]+a
    cases.append({"name": "translated", "stations": shifted_s, "u": p/np.linalg.norm(p),
                  "g": 1/np.linalg.norm(p), "y": base["y"], "qr": qr})
    wls = []
    for case in cases:
        solved = solve_mpr_wls(case["y"], case["stations"], qr, max_nfev=100)
        wls.append({"name": case["name"], "success": solved.success, "u": solved.u.tolist(), "g": solved.g,
                    "direction_chord": float(np.linalg.norm(solved.u-case["u"])), "g_error": float(solved.g-case["g"]),
                    "forward_residual_norm_m": float(np.linalg.norm(range_differences(solved.u, solved.g, case["stations"])-case["y"])),
                    "objective": solved.objective, "selected_nfev": solved.nfev})
    result["numerical_wls_deterministic"] = wls
    fixtures = {"stations": np.stack([c["stations"] for c in cases]), "u": np.stack([c["u"] for c in cases]),
                "g": np.array([c["g"] for c in cases]), "y": np.stack([c["y"] for c in cases]), "qr": qr,
                "names": np.array([c["name"] for c in cases], dtype=object),
                "noise": rng.normal(size=(32, 7))@np.linalg.cholesky(qr).T}
    bound = local_information(base["u"], base["g"], s0, qr)
    fixtures.update(expected_direction_bound=bound.direction_trace, expected_g_bound=bound.inverse_range_variance)
    run = ROOT/"runs/initial_review"; run.mkdir(parents=True, exist_ok=True)
    savemat(run/"matlab_inputs.mat", fixtures)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/"python_checks.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
