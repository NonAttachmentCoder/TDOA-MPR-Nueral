"""Archived eight-receiver nonlinear WLS diagnostic from the initial review.

This module is NOT the Wang-Ho MLE implementation or the Sun-Ho-Wan GTRS,
SUM, NSP or NSPBS. Any claim of source-paper fidelity requires a separate,
frozen MATLAB-vs-Python qualification. With uncertain receiver locations,
the objective is a pseudo-likelihood because it omits log det C(u,g).
"""
from dataclasses import dataclass
import numpy as np
from scipy.optimize import least_squares
from scipy.linalg import solve_triangular
from .physics import range_differences, mpr_jacobians
from .covariance import effective_covariance, validate_spd


def _normalize(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-10 else np.array([1.0, 0.0, 0.0])


def _angles(u):
    return np.array([np.arctan2(u[1], u[0]),
                     np.arctan2(u[2], np.hypot(u[0], u[1]))])


def _u(az, el):
    return np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])


@dataclass
class WLSResult:
    u: np.ndarray
    g: float
    success: bool
    objective: float
    nfev: int
    message: str


def solve_mpr_wls(y, stations, qr, qs=None, max_nfev=150):
    """Fit azimuth, elevation and signed dimensionless g*aperture.

    Uses multiple deterministic starts and scipy least_squares. The algorithm
    is an original numerical check, not a faithful published TDOA baseline.
    """
    s = np.asarray(stations, dtype=float)
    y = np.asarray(y, dtype=float)
    if s.shape != (8, 3) or y.shape != (7,):
        raise ValueError("expected stations [8,3] and TDOA [7]")
    qr = validate_spd(qr, "qr")
    if qr.shape != (7, 7):
        raise ValueError("qr must be [7,7]")
    if qs is not None and np.asarray(qs).shape != (24, 24):
        raise ValueError("qs must be [24,24]")
    scale = max(float(np.sqrt(np.mean(np.sum((s - s.mean(0))**2, axis=1)))), 1.0)
    delta = s[1:] - s[0]
    initial = _normalize(-np.linalg.lstsq(delta, y, rcond=None)[0])
    starts = [_angles(initial), _angles(-initial)]
    guesses = [(a[0], a[1], z) for a in starts for z in (0.0, 0.25, 1.0)]
    # Periodic azimuth is unbounded, avoiding a spurious wrap boundary.
    lower, upper = np.array([-np.inf, -np.pi/2, -4.]), np.array([np.inf, np.pi/2, 4.])

    def residual(z):
        direction = _u(z[0], z[1])
        inv_range = z[2] / scale
        dif = y - range_differences(direction, inv_range, s)
        jac = mpr_jacobians(direction, inv_range, s)
        C = effective_covariance(qr, jac.ds, qs)
        chol = np.linalg.cholesky(C)
        return solve_triangular(chol, dif, lower=True)

    best = None
    for guess in guesses:
        try:
            res = least_squares(residual, guess, bounds=(lower, upper),
                                max_nfev=max_nfev, ftol=1e-10, xtol=1e-10, gtol=1e-10)
            objective = 0.5 * res.fun @ res.fun
            if best is None or objective < best[0]:
                best = (float(objective), res)
        except (ValueError, np.linalg.LinAlgError, FloatingPointError):
            continue
    if best is None:
        return WLSResult(np.full(3, np.nan), np.nan, False, np.inf, 0, "all starts failed")
    obj, res = best
    return WLSResult(_u(res.x[0], res.x[1]), float(res.x[2] / scale),
                     bool(res.success), obj, int(res.nfev), str(res.message))
