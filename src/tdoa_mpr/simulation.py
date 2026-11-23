"""Development frames in meters, differenced against receiver 0."""
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import numpy as np
from .physics import range_differences
from .covariance import differencing_matrix, range_difference_covariance

SUN2019 = json.loads(Path(__file__).with_name("sun2019_design.json").read_text())
_STATIONS_M = 1000 * np.asarray(SUN2019["stations_km"])
_RANGES_M = 1000 * np.union1d(SUN2019["range"]["range_km"], SUN2019["noise"]["range_km"])
_VARIANCES_DB = np.array(SUN2019["noise"]["tdoa_variance_db"])


@dataclass(frozen=True)
class SimulationConfig:
    """Seven known stations, Gaussian marginal TDOA variance from the 2019 grid."""
    n_receivers: int = 7
    reference: int = 0
    outlier_probability: float = 0.0
    outlier_std_multiplier: float = 8.0
    positive_delay_bias_probability: float = 0.0
    positive_delay_bias_m: float = 5.0

    def __post_init__(self):
        if self.n_receivers != 7 or self.reference != 0:
            raise ValueError("the Sun 2019 design uses seven stations, reference 0")
        if not 0 <= self.outlier_probability <= 1 or not 0 <= self.positive_delay_bias_probability <= 1:
            raise ValueError("invalid contamination probability")

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class LegacyEightReceiverConfig:
    """Archived eight-station generator for old checkpoints and the initial audit."""
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


def _legacy_geometry(rng, config):
    n = config.n_receivers
    L = _log_uniform(rng, config.aperture_low_m, config.aperture_high_m)
    s_true = rng.normal(size=(n, 3)) * L / np.sqrt(3)
    s_true[0] = 0.0  # fixed global-origin convention in the generator
    direction = rng.normal(size=3)
    direction /= np.linalg.norm(direction)
    r = _log_uniform(rng, config.range_low_m, config.range_high_m)

    arrival_sigma = _log_uniform(rng, config.arrival_sigma_low_m, config.arrival_sigma_high_m)
    arrival_sigmas = arrival_sigma * rng.uniform(0.7, 1.3, size=n)
    q_toa = np.diag(arrival_sigmas**2)
    qr = range_difference_covariance(q_toa, config.reference)

    position_sigma = rng.uniform(config.position_sigma_low_m, config.position_sigma_high_m)
    position_sigmas = position_sigma * rng.uniform(0.7, 1.3, size=n)
    qs = np.diag(np.repeat(position_sigmas**2, 3))
    s_reported = s_true + rng.normal(size=(n, 3)) * position_sigmas[:, None]
    return s_true, s_reported, direction, r, arrival_sigmas, qr, qs


def sample_frame(rng, config=SimulationConfig()):
    """Draw one development frame. Exact figure ensembles use run_cisp_sweep.m."""
    n = config.n_receivers
    if isinstance(config, LegacyEightReceiverConfig):
        s_true, s_reported, direction, r, arrival_sigmas, qr, qs = _legacy_geometry(rng, config)
    else:
        s_true = _STATIONS_M.copy()
        s_reported = s_true.copy()
        direction = rng.normal(size=3)
        direction /= np.linalg.norm(direction)
        r = float(rng.choice(_RANGES_M))
        variance = 10.0 ** (rng.choice(_VARIANCES_DB) / 10.0)
        arrival_sigmas = np.full(n, np.sqrt(variance / 2))
        qr = variance * (np.eye(n-1) + np.ones((n-1,n-1))) / 2
        qs = np.zeros((3*n, 3*n))
    g = 1.0 / r

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
