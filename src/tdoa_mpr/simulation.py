"""Synthetic *range-difference* measurements for independent research pilots.

Random generation is per frame with a common reference-receiver error.
These development recipes are not calibrated reconstructions of published
figures and should not be reported as independent confirmation evidence.
"""
from dataclasses import dataclass, asdict
import numpy as np
from .physics import range_differences
from .covariance import differencing_matrix, range_difference_covariance


@dataclass(frozen=True)
class SimulationConfig:
    n_receivers: int = 8
    reference: int = 0
    aperture_low_m: float = 25.0
    aperture_high_m: float = 75.0
    range_low_m: float = 60.0
    range_high_m: float = 80000.0
    arrival_sigma_low_m: float = 0.05
    arrival_sigma_high_m: float = 1.0
    position_sigma_low_m: float = 0.02
    position_sigma_high_m: float = 0.7
    outlier_probability: float = 0.0
    outlier_std_multiplier: float = 8.0
    positive_delay_bias_probability: float = 0.0
    positive_delay_bias_m: float = 5.0

    def __post_init__(self):
        if self.n_receivers != 8 or self.reference != 0:
            raise ValueError("v0 neural protocol is 8 receivers, reference 0")
        if not (0 < self.aperture_low_m <= self.aperture_high_m):
            raise ValueError("invalid aperture interval")
        if not (0 < self.range_low_m < self.range_high_m):
            raise ValueError("invalid distance interval")
        if not (0 < self.arrival_sigma_low_m <= self.arrival_sigma_high_m):
            raise ValueError("arrival sigma must be positive")
        if not (0 <= self.position_sigma_low_m <= self.position_sigma_high_m):
            raise ValueError("position sigma must be nonnegative")
        if not 0 <= self.outlier_probability <= 1 or not 0 <= self.positive_delay_bias_probability <= 1:
            raise ValueError("invalid contamination probability")

    def to_dict(self):
        return asdict(self)


def _log_uniform(rng, low, high):
    if low == high:
        return float(low)
    return float(np.exp(rng.uniform(np.log(low), np.log(high))))


def sample_frame(rng, config=SimulationConfig()):
    """Return inference inputs plus separately marked private truth."""
    n = config.n_receivers
    L = _log_uniform(rng, config.aperture_low_m, config.aperture_high_m)
    s_true = rng.normal(size=(n, 3)) * L / np.sqrt(3)
    s_true[0] = 0.0  # fixed global-origin convention in the generator
    direction = rng.normal(size=3)
    direction /= np.linalg.norm(direction)
    r = _log_uniform(rng, config.range_low_m, config.range_high_m)
    g = 1.0 / r

    arrival_sigma = _log_uniform(rng, config.arrival_sigma_low_m, config.arrival_sigma_high_m)
    arrival_sigmas = arrival_sigma * rng.uniform(0.7, 1.3, size=n)
    q_toa = np.diag(arrival_sigmas**2)
    qr = range_difference_covariance(q_toa, config.reference)

    position_sigma = rng.uniform(config.position_sigma_low_m, config.position_sigma_high_m)
    position_sigmas = position_sigma * rng.uniform(0.7, 1.3, size=n)
    qs = np.diag(np.repeat(position_sigmas**2, 3))
    s_reported = s_true + rng.normal(size=(n, 3)) * position_sigmas[:, None]

    arrival_error = rng.normal(size=n) * arrival_sigmas
    if config.outlier_probability:
        mask = rng.random(n) < config.outlier_probability
        extra = rng.normal(size=n) * arrival_sigmas * np.sqrt(max(0.0, config.outlier_std_multiplier**2 - 1.0))
        arrival_error += mask * extra
    if config.positive_delay_bias_probability:
        mask = rng.random(n) < config.positive_delay_bias_probability
        arrival_error += mask * config.positive_delay_bias_m
    noise = differencing_matrix(n, config.reference) @ arrival_error
    clean = range_differences(direction, g, s_true, config.reference)
    return {
        "y": clean + noise,
        "stations": s_reported,
        "qr": qr,
        "qs": qs,
        "u": direction,
        "g": np.float64(g),
        "r": np.float64(r),
        "s_true": s_true,
        "clean_y": clean,
        "arrival_error": arrival_error,
    }


def sample_batch(rng, batch_size, config=SimulationConfig()):
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    frames = [sample_frame(rng, config) for _ in range(batch_size)]
    return {key: np.stack([frame[key] for frame in frames])
            for key in frames[0]}
