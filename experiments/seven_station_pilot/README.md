# Seven-station Gaussian pilot

The two MATLAB R2024a files contain the six range differences, receiver coordinates, full measurement covariance, zero station covariance, source parameters, random stream, four estimators' framewise outputs, warnings and errors. Each point uses 32 centered Gaussian draws. The noise sweep evaluates 10 points, the distance sweep 25. The standardized draws are reused across points and both sweeps. [Noise data](noise_32.mat) · [Distance data](range_32.mat) · [Noise scores](noise_32.json) · [Distance scores](range_32.json) · [All 11 panels in one PDF](TDOA_sweeps_32_frames.pdf)

## Reproduce the manuscript figures

Run from the repository root after installing the project with its plot extra. The following commands score the saved frames, write fresh JSON files and render both figure families.

```sh
python -m tdoa_mpr.evaluate --sweep experiments/seven_station_pilot/noise_32.mat --figures runs/replot/fig --output runs/replot/noise_32.json
python -m tdoa_mpr.evaluate --sweep experiments/seven_station_pilot/range_32.mat --figures runs/replot/fig --output runs/replot/range_32.json
```

To regenerate the observations and estimator outputs in a fresh location, run the following MATLAB command from the repository root. Both source ZIP hashes are embedded in the MAT files. The scored JSON records the SHA-256 of its exact input MAT. A rerun can give an equivalent MAT with a different header timestamp.

```sh
matlab -singleCompThread -batch "addpath('experiments'); run_cisp_sweep('noise',32,'runs/reproduce/noise_32.mat'); run_cisp_sweep('range',32,'runs/reproduce/range_32.mat')"
```

For metric MSE and corresponding bound B, the paper reports the gap as 10 log₁₀(MSE/B). In each JSON the first CRLB row is the angular coordinate trace and the second is the inverse-range variance in m⁻². If range is r meters, the relative radial standard-deviation bound in percent is 100 r √Bgg. At 20, 300 and 460 km the published noise setting is 1 m². The resulting values are 2.07%, 30.27% and 46.39%. [Paper Figure 1](../../paper/fig/) · [Estimator attribution](../../baselines/SOURCES.md)

## Reproduce the wavefront separation in Table I

Run the following command from the repository root. It reads the geometry, bearing, nominal covariances, ranges and analytical bounds in the two saved MAT files.

```sh
python experiments/seven_station_pilot/wavefront_separation.py
```

Each output row gives the minimum Mahalanobis distance from the finite-range mean to any unit plane-wave mean, its first-order approximation at zero inverse range, and the relative standard-deviation bound at the finite range. The two distances are dimensionless. The last column is a percentage. The `range` rows for 5, 20, 100, 300 and 460 km reproduce Table I. The `noise` rows reproduce the separations at 15 km quoted in the text. These calculations use the seven known receivers with receiver 0 as reference, six predicted differences in meters and the full 6×6 covariance in m².
