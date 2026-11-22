"""Numerically stable known-speed 3-D TDOA in modified polar representation.

All observations are *range differences* in meters. The state origin remains
the fixed Cartesian origin even when the reporting reference station is noisy.
Analytic derivatives are with respect to the unit-sphere ambient coordinate,
the signed inverse range, and each reported receiver coordinate.
"""
from dataclasses import dataclass
import numpy as np

_EPS = 1e-12


def _inputs(u, g, stations, ref):
    s = np.asarray(stations, dtype=np.float64)
    u = np.asarray(u, dtype=np.float64)
    if s.ndim != 2 or s.shape[1] != 3 or s.shape[0] < 4:
        raise ValueError("stations must have shape [M>=4,3]")
    if u.shape != (3,) or not np.isfinite(u).all():
        raise ValueError("u must be a finite three-vector")
    n = np.linalg.norm(u)
    if n < _EPS:
        raise ValueError("u has zero norm")
    if not np.isfinite(s).all() or not np.isfinite(g):
        raise ValueError("nonfinite geometry or inverse range")
    if not 0 <= ref < len(s):
        raise ValueError("reference station index out of range")
    return u / n, float(g), s, np.arange(s.shape[0]) != ref


def range_differences(u, g, stations, ref=0):
    """Return M-1 predicted r_i-r_ref (meters); valid exactly at g=0.

    Negative g is smooth analytical continuation, not physical negative range.
    """
    u, g, s, take = _inputs(u, g, stations, ref)
    delta = s[take] - s[ref]
    ai = np.linalg.norm(u - g * s[take], axis=1)
    a0 = np.linalg.norm(u - g * s[ref])
    denom = ai + a0
    if np.any(denom <= _EPS):
        raise ValueError("degenerate coincidence makes MPR continuation undefined")
    num = -2.0 * (delta @ u) + g * (
        np.einsum("ij,ij->i", s[take], s[take]) - (s[ref] @ s[ref]))
    return num / denom


def tangent_basis(u):
    """Deterministic 3x2 orthonormal basis for the local tangent plane."""
    u = np.asarray(u, dtype=np.float64)
    u = u / np.linalg.norm(u)
    axis = np.zeros(3)
    axis[np.argmin(np.abs(u))] = 1.0
    e1 = np.cross(u, axis)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(u, e1)
    return np.column_stack((e1, e2))


@dataclass
class MPRJacobians:
    du: np.ndarray   # [M-1,3], ambient normalized-u extension
    dg: np.ndarray   # [M-1], signed g
    ds: np.ndarray   # [M-1,3M], s0x,s0y,s0z,... ordering


def mpr_jacobians(u, g, stations, ref=0):
    """Closed-form derivatives of the rationalized range-difference map."""
    u, g, s, take = _inputs(u, g, stations, ref)
    inds = np.flatnonzero(take)
    si, s0 = s[take], s[ref]
    vi_raw, v0_raw = u - g * si, u - g * s0
    ai, a0 = np.linalg.norm(vi_raw, axis=1), np.linalg.norm(v0_raw)
    if np.any(ai <= _EPS) or a0 <= _EPS:
        raise ValueError("derivative undefined at sensor/source coincidence")
    vi, v0 = vi_raw / ai[:, None], v0_raw / a0
    delta = si - s0
    q_delta = np.einsum("ij,ij->i", si, si) - s0 @ s0
    num = -2 * (delta @ u) + g * q_delta
    den = ai + a0
    den2 = den * den

    dn_du = -2 * delta
    dd_du = vi + v0
    du = (dn_du * den[:, None] - num[:, None] * dd_du) / den2[:, None]
    dd_dg = -np.einsum("ij,ij->i", vi, si) - v0 @ s0
    dg = (q_delta * den - num * dd_dg) / den2

    ds = np.zeros((len(inds), 3 * len(s)), dtype=np.float64)
    dref_num = 2 * u - 2 * g * s0
    dref_den = -g * v0
    dref = (dref_num * den[:, None] - num[:, None] * dref_den) / den2[:, None]
    dself_num = -2 * u[None, :] + 2 * g * si
    dself_den = -g * vi
    dself = (dself_num * den[:, None] - num[:, None] * dself_den) / den2[:, None]
    for row, station in enumerate(inds):
        ds[row, 3 * station:3 * station + 3] = dself[row]
        ds[row, 3 * ref:3 * ref + 3] = dref[row]
    return MPRJacobians(du=du, dg=dg, ds=ds)


@dataclass
class LocalBound:
    information: np.ndarray
    covariance: np.ndarray
    direction_trace: float
    inverse_range_variance: float
    condition: float
    valid: bool


def local_information(u, g, stations, qr, qs=None, ref=0, max_condition=1e12):
    """Linearized [tangent direction (2), inverse range] information.

    Conditional Gaussian CRLB when qs is zero; otherwise first-order propagated
    nuisance-position approximation, not an exact finite-noise CRLB.
    """
    from .covariance import effective_covariance
    j = mpr_jacobians(u, g, stations, ref=ref)
    E = tangent_basis(u)
    H = np.column_stack((j.du @ E, j.dg))
    C = effective_covariance(qr, j.ds, qs)
    F = H.T @ np.linalg.solve(C, H)
    F = 0.5 * (F + F.T)
    eig = np.linalg.eigvalsh(F)
    condition = float(np.inf if eig[0] <= 0 else eig[-1] / eig[0])
    valid = bool(eig[0] > 0 and condition < max_condition)
    cov = np.linalg.inv(F) if valid else np.full((3, 3), np.nan)
    return LocalBound(F, cov, float(np.trace(cov[:2, :2])),
                      float(cov[2, 2]), condition, valid)
