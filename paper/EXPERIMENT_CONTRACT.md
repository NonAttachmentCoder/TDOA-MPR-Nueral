# TDOA–MPR experiment contract

The two primary Gaussian comparisons use the seven fixed 3-D receivers in Sun, Ho and Wan's 2019 MATLAB example. Receiver 0 is at the origin. The source has azimuth 22.13° and elevation 14.41°. The station coordinates are in km in the design file and are multiplied by 1000 for the experiment. All methods receive six range differences in m, the same reported stations and the full nominal measurement covariance in m². The station-position covariance is zero (21×21) and is supplied to the methods whose interface accepts it. [Original example](../baselines/matlab/sun2019/Example.m) · [Machine-readable settings](../src/tdoa_mpr/sun2019_design.json)

| Group | Horizontal axis | Fixed value | Original frames per point | Panels from the source script |
|---|---|---|---:|---|
| Noise | −40 to 50 dB in steps of 10 dB (10 points) | Range 15 km | 1000 | Angle, inverse-range, Cartesian-position and range MSE. Angle, inverse-range and position bias magnitudes. |
| Distance | 5, 10, 20, 40, …, 460 km (25 points) | Marginal TDOA variance 1 m² (0 dB) | 2000 | Angle and inverse-range MSE and bias magnitudes. |

For axis value d, the variance of one range difference is v = 10^(d/10) m². The seven independent receiver-arrival errors each have variance v/2. Differencing against receiver 0 gives a dense 6×6 Qr with v on the diagonal and v/2 elsewhere. The source script uses MATLAB's default random stream, subtracts the sample mean of the differenced noise, and reuses the draws at each grid point. This couples frames within a finite ensemble and pairs the sweep points. Nominal CRLB curves use Qr as supplied to the original script. Confidence intervals intended for independent ensembles require independent repetitions that respect this sampling design.

## Estimators and reporting

Use the original DeviceIoT SCO, SUM and GTRS and the CISP Chan–Ho Cartesian estimator, each on the same observation with its released settings. Save native signed MPR estimates and Cartesian positions, exceptions and warnings. For Chan–Ho the scored direction is the unit displacement from receiver 0 and g is its reciprocal length. The native Cartesian position supplies the position metrics. A zero displacement makes the derived MPR undefined. A nonfinite or complex metric produces a missing aggregate for that method and grid point. Finite large errors remain in the mean. Record valid and failed counts with each curve. [Estimator provenance](../baselines/SOURCES.md)

The source angle MSE is the mean squared azimuth error plus mean squared elevation error (rad²) and its CRLB is the sum of those two coordinate variances. Inverse-range MSE is in m⁻². The plotting program applies 10 log₁₀ to the linear MSE or bound and 20 log₁₀ to the bias magnitude. The example's angle-bias statistic uses the mean absolute angle coordinates before subtracting the true angles. Positions use each estimator's native Cartesian output and the range diagnostic uses its signed reciprocal inverse range. The 2019 analytical SUM/GTRS bias curves are labelled by source year. All empirical curves use their own method's outputs, including GTRS angle MSE against distance and GTRS position bias against noise. The project also records the squared spherical angle separately.

The neural comparison reads the same MAT file and requires a seven-receiver checkpoint. The public geometry and test direction are fixed. Development training samples directions across the sphere and draws range and noise level independently. These two sweeps measure performance **conditional on one layout and bearing**. They cannot establish generalization across geometries, sensitivity to varying covariance correlations or robustness to position error.

## Further scientific questions

Separate receiver-level outliers, a faulty reference, excess delays and position-report mismatch remain prospective stress tests. Under station mismatch, Chan–Ho uses reported receiver positions and its native known-station weighting. Matched neural ablations and timing remain prospective. The fixed nominal experiment has Qs=0 and constant pairwise TDOA correlation 1/2. Testing whether a learned method adapts to other covariance structures requires additional evidence.

The working manuscript reports the completed 32-frame classical pilot and its nominal bounds. Plots identify the frame count. The full source ensembles, neural comparisons and independent confirmation remain prospective. A frozen-first-query control would hold the first predicted differences and local receiver directions fixed during the final recurrent pass while updating the other state inputs. [Saved pilot](../experiments/seven_station_pilot/) · [Run instructions](../experiments/README.md)
