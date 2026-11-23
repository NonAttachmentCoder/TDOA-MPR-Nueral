# Classical baseline sources

The three MPR estimators, **SCO, SUM and GTRS**, come from the CISP release dated April 12, 2022. The three MATLAB files under `matlab/device_iot/private/` were copied byte for byte. MATLAB resolves these private functions from the adjacent project driver, including when the 2019 functions of the same names are on the path. [Author listing](https://cisp.ece.missouri.edu/code.html) · [DeviceIoT ZIP](https://cisp.ece.missouri.edu/code/TDOALocDeviceIoT/TDOALocDeviceIoT.zip) · [Lab license](matlab/device_iot/CISP_LICENSE.txt)

| Official file | SHA-256 |
|---|---|
| TDOALocDeviceIoT.zip | `070aeeafbe248fd1f61207929718f1670d7469b4664882e4dfb42b9a04d6f975` |
| TDOA_SCO_MPR.m | `731b5133adca77f039c1cdc61e11924a3e168b00581f5a04b5f5b572e3484f39` |
| TDOA_SUM_MPR.m | `0f29d5bbe7534400e67c0fc533a5e151472e29b318d351a937eecc984bcf8ec9` |
| TDOA_GTRS_MPR.m | `e54fd8aae12b1ce168451c7c1083b1dcb68aae49bda1bbb719888e158c554fc5` |

Cite Y. Sun, K. C. Ho, G. Wang, H. Chen, Y. Yang, L. Chen and Q. Wan, “Computationally Attractive and Location Robust Estimator for IoT Device Positioning,” *IEEE Internet of Things Journal*, 9(13), 10891–10907, July 2022. The bibliographic author list follows the published article. [Paper](https://doi.org/10.1109/JIOT.2021.3127690)

The Cartesian baseline is Y. T. Chan and K. C. Ho, “A Simple and Efficient Estimator for Hyperbolic Location,” *IEEE TSP*, 42(8), 1905–1915, 1994. CISP distributes the 3-D-capable `TDOALoc.m`, credited in its header to Ming Sun and K. C. Ho, revised October 2010. The distribution uses three first-stage weight updates and its own second-stage sign and fallback rules. It takes the station columns, reference-1 range differences in m and their full covariance in m², and returns an absolute Cartesian position. [Paper](https://doi.org/10.1109/78.301830) · [CISP ZIP](https://cisp.ece.missouri.edu/code/TDOALoc/TDOALoc.zip) · [Released function](matlab/chan_ho1994/private/TDOALoc.m) · [License](matlab/chan_ho1994/CISP_LICENSE.txt)

The ZIP SHA-256 is `0f04fd45e5c0f844b45b577f738340e662a1278467f8936c8d596274d1fd4de8`. The vendored function matches both the archive member and the standalone CISP download, SHA-256 `4fd055ebb10185d37658f51b2e1f9f640b934ebba89d98697f3a69b52dfc160d`.

The scenario, noise model, figure conventions, CRLB and 2019 bias reference functions come from Sun, Ho and Wan, *IEEE TSP*, 67(2), 320–335. The official scenario ZIP has SHA-256 `e8551e410310384f7c7fb015c96cde9109eabce92d3a85e5083d12a423e407ef`. The vendored Example.m has SHA-256 `fd97718364586e54693281ff2bb85ce9d8b91acca8eba68f051700b0eb0f45fe`. [Paper](https://doi.org/10.1109/TSP.2018.2879622) · [Scenario ZIP](https://cisp.ece.missouri.edu/code/TDOALoc_AlgbSolMPR/TDOALoc_AlgbSolMPR.zip) · [2019 source verification](matlab/sun2019/PROVENANCE.md)

The 2017 and 2019 estimator snapshots and previous WLS diagnostic outputs remain available to reproduce the dated initial review. Its negative-elevation SUM observation concerns the 2019 implementation. DeviceIoT's SUM uses a signed atan2 elevation formula and accepts station covariance. [Historical review](../docs/INITIAL_TECHNICAL_REVIEW.md)
