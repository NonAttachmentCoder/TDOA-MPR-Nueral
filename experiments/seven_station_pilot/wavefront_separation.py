"""Reproduce the plane-wave distances from the geometry in the two saved sweeps."""
from pathlib import Path

import numpy as np
from scipy.io import loadmat
from scipy.optimize import brentq

from tdoa_mpr.physics import mpr_jacobians, range_differences, tangent_basis


def plane_wave_distance(baselines, mean, chol):
    """Minimum Mahalanobis distance from the finite-range mean to a unit plane wave."""
    design = np.linalg.solve(chol, baselines)
    target = np.linalg.solve(chol, -mean)
    # A common scale makes the multiplier independent of the noise power.
    scale = np.linalg.norm(design, ord=2)
    design, target = design / scale, target / scale
    eig, basis = np.linalg.eigh(design.T @ design)
    coeff = basis.T @ (design.T @ target)

    def norm_error(multiplier):
        return np.linalg.norm(coeff / (eig + multiplier)) - 1

    # For this array and bearing the root is strictly above -eig[0].
    # The shifted Hessian is then positive definite, certifying a global minimum.
    left = np.nextafter(-eig[0], np.inf)
    root = brentq(norm_error, left, np.linalg.norm(coeff), xtol=1e-15)
    direction = basis @ (coeff / (eig + root))
    return scale * np.linalg.norm(design @ direction - target)


def evaluate(path):
    data = loadmat(path, simplify_cells=True,
                   variable_names=["stations", "angles", "Qr", "range_m", "variance_db", "crlb"])
    stations = data["stations"].T
    baselines = stations[1:] - stations[0]
    az, el = data["angles"]
    u = np.array([np.cos(az)*np.cos(el), np.sin(az)*np.cos(el), np.sin(el)])
    j0 = mpr_jacobians(u, 0, stations, ref=0)
    angular = j0.du @ tangent_basis(u)
    for k, distance in enumerate(data["range_m"]):
        chol = np.linalg.cholesky(data["Qr"][:, :, k])
        mean = range_differences(u, 1 / distance, stations, ref=0)
        exact = plane_wave_distance(baselines, mean, chol)
        A, b = np.linalg.solve(chol, angular), np.linalg.solve(chol, j0.dg)
        residual = b - A @ np.linalg.lstsq(A, b, rcond=None)[0]
        linear = np.linalg.norm(residual) / distance
        relative_bound = distance * np.sqrt(data["crlb"][1, k])
        yield distance / 1000, data["variance_db"][k], exact, linear, 100 * relative_bound


if __name__ == "__main__":
    print("sweep,range_km,variance_db,d_plane,d_first_order,relative_sd_bound_pct")
    for sweep in ("noise", "range"):
        path = Path(__file__).with_name(f"{sweep}_32.mat")
        for row in evaluate(path):
            print(sweep, *(f"{value:.8g}" for value in row), sep=",")
