# Seven-receiver TDOA experiments

The manuscript uses the saved 32-frame pilot. Its raw inputs, original estimator outputs, scores, full figure set and regeneration commands are available in the [pilot directory](seven_station_pilot/).

From the checkout root, generate a small paired MATLAB file for each figure family and score it with the project Python environment. Each command below uses four draws per grid point as a development check.

```bash
matlab -batch "addpath('experiments'); run_cisp_sweep('noise',4,'runs/cisp/noise_4.mat'); run_cisp_sweep('range',4,'runs/cisp/range_4.mat')"
python -m tdoa_mpr.evaluate --sweep runs/cisp/noise_4.mat --figures runs/cisp/figures --output runs/cisp/noise_4.json
python -m tdoa_mpr.evaluate --sweep runs/cisp/range_4.mat --figures runs/cisp/figures --output runs/cisp/range_4.json
```

MATLAB runs the official DeviceIoT SCO, SUM and GTRS and the Chan–Ho Cartesian estimator on the same six reference-0 distance differences in meters. Each MAT contains the observations, fixed positions, dense Qr, zero Qs, raw outputs, per-call exceptions and last warnings, bounds, RNG state, MATLAB version and the source archive digests. The JSON reports linear error metrics and counts per method and point. Pre-existing three-method files can still be scored using the columns they contain. Install the plotting dependency with `python -m pip install -e '.[plot]'`. Append `--checkpoint path/to/model.pt` to score a seven-station model on the exact observations.

The DMPR paper demo places azimuth/elevation above inverse range. Its empirical estimates use markers and its CRLB is a dark red line. The Cartesian series uses the cyan plus from its two-stage Cartesian WLS slot. The style reference is the archived `main_gongw111_gnmprv_paper_demo.m` and `plotConfigDefault.mat` (configuration SHA-256 `a6023841009bc27771a449a0c26b7bd011f170a2de2db369d35e7526f312c06b`). The TDOA plots retain the 2019 measurement units, bounds and bias definitions. Each sweep exports `mpr_mse_*` and `mpr_bias_*` in vector PDF and PNG. The noise sweep also exports `position_range_mse_noise` and `position_bias_noise`, covering all 11 original panels.

For the 32-frame development figures use 32 in both MATLAB calls and fresh output paths. The original counts are 1000 for `noise` and 2000 for `range`, totaling 60,000 frames and 240,000 calls with four baselines. The example's random stream is public and its noise bank is mean-centered. For N centered draws the marginal variance of one draw is (N−1)/N times its nominal variance. [Design, metrics and inference scope](../paper/EXPERIMENT_CONTRACT.md) · [Baseline versions](../baselines/SOURCES.md)
