"""Reference-star TDOA covariance and first-order station-error propagation."""
import numpy as np


def differencing_matrix(n_receivers=8, ref=0):
    if n_receivers < 2 or not 0 <= ref < n_receivers:
        raise ValueError("invalid number/reference of receivers")
    d = np.zeros((n_receivers - 1, n_receivers), dtype=np.float64)
    keep = [i for i in range(n_receivers) if i != ref]
    for row, receiver in enumerate(keep):
        d[row, receiver] = 1.0
        d[row, ref] = -1.0
    return d


def range_difference_covariance(q_toa, ref=0, propagation_speed=None):
    """Covariance of D e in m².

    q_toa is receiver-arrival *range* covariance (m²), or seconds² if
    propagation_speed (m/s) is specified, in which case convert by c².
    """
    q = np.asarray(q_toa, dtype=np.float64)
    if q.ndim != 2 or q.shape[0] != q.shape[1]:
        raise ValueError("q_toa must be square")
    D = differencing_matrix(q.shape[0], ref)
    factor = 1.0 if propagation_speed is None else float(propagation_speed) ** 2
    return factor * (D @ q @ D.T)


def effective_covariance(qr, js, qs=None):
    """C=Qr+Js Qs Js^T, first-order station uncertainty propagation."""
    qr = np.asarray(qr, dtype=np.float64)
    js = np.asarray(js, dtype=np.float64)
    if qr.shape != (js.shape[0], js.shape[0]):
        raise ValueError("qr / Jacobian size mismatch")
    if qs is None:
        return qr.copy()
    qs = np.asarray(qs, dtype=np.float64)
    if qs.shape != (js.shape[1], js.shape[1]):
        raise ValueError("qs / Jacobian size mismatch")
    c = qr + js @ qs @ js.T
    return (c + c.T) / 2


def validate_spd(c, name="covariance"):
    arr = np.asarray(c, dtype=np.float64)
    if arr.ndim != 2 or arr.shape[0] != arr.shape[1] or not np.isfinite(arr).all():
        raise ValueError(f"{name} must be finite and square")
    np.linalg.cholesky(arr)
    return arr
