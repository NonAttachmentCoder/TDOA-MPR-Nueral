import tempfile
import unittest
from importlib.util import find_spec
from pathlib import Path
from unittest.mock import patch

import numpy as np
from scipy.io import savemat

from tdoa_mpr.sweeps import evaluate_sweep, plot_sweep


class TestPublishedSweep(unittest.TestCase):
    def test_method_columns_signed_range_and_failed_frames(self):
        # Axes follow the saved MATLAB file: coordinate, method, frame, point.
        mpr = np.zeros((3, 4, 2, 2))
        mpr[2] = 0.01
        mpr[0, 1] = 0.2
        mpr[1, 2] = -0.3
        mpr[2, 1, 0, 0] = -0.01
        mpr[0, 2, 1, 1] = np.nan
        mpr[2, 3] = 0.02
        pos = np.zeros_like(mpr)
        pos[0] = 100
        pos[2, 2] = 7
        pos[0, 3] = 50
        errors = np.full((4, 2, 2), "", dtype=object)
        errors[2, 1, 1] = "fixture: missing angle"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"fixture.mat"
            fixture = dict(
                sweep="noise", range_m=[100., 100.], angles=[0., 0.], variance_db=[0., 10.],
                ensembles=2, official_ensembles=1000,
                method_names=np.array(["SCO", "SUM", "GTRS", "Chan-Ho"], dtype=object),
                mpr=mpr, position=pos, errors=errors, warnings=np.full_like(errors, ""),
                matlab_release="fixture", device_iot_zip_sha256="fixture",
                chan_ho_zip_sha256="cartesian-source", crlb=np.ones((4,2)),
                bias_2019=np.zeros((3,2,2)))
            savemat(path, fixture)
            result = evaluate_sweep(path)
            self.assertEqual(result["chan_ho_zip_sha256"], "cartesian-source")
            methods = result["methods"]
            self.assertEqual(methods["Chan-Ho"]["position_mse_m2"], [2500., 2500.])
            self.assertEqual(methods["Chan-Ho"]["negative_g"], [0, 0])
            # Archived three-method MAT files still expose exactly their saved outputs.
            for key in ("mpr", "position"):
                fixture[key] = fixture[key][:, :3]
            for key in ("method_names", "errors", "warnings"):
                fixture[key] = fixture[key][:3]
            del fixture["chan_ho_zip_sha256"]
            savemat(path, fixture)
            legacy = evaluate_sweep(path)
            self.assertEqual(list(legacy["methods"]), ["SCO", "SUM", "GTRS"])
            self.assertNotIn("chan_ho_zip_sha256", legacy)
        self.assertEqual(methods["SCO"]["angle_mse_rad2"], [0., 0.])
        np.testing.assert_allclose(methods["SUM"]["angle_mse_rad2"], [0.04, 0.04])
        self.assertAlmostEqual(methods["GTRS"]["angle_mse_rad2"][0], 0.09)
        self.assertIsNone(methods["GTRS"]["angle_mse_rad2"][1])
        self.assertEqual(methods["GTRS"]["errors"], [0, 1])
        self.assertEqual(methods["GTRS"]["valid_mpr"], [2, 1])
        self.assertEqual(methods["GTRS"]["position_bias_m"], [7., 7.])
        self.assertEqual(methods["SUM"]["negative_g"], [1, 0])
        self.assertAlmostEqual(methods["SUM"]["g_mse_mminus2"][0], 0.0002)

    @unittest.skipUnless(find_spec("matplotlib"), "plot extra is required")
    def test_paired_panels_keep_cartesian_and_optional_network(self):
        names = ["SCO", "SUM", "GTRS", "Chan-Ho", "Neural"]
        metrics = ["angle_mse_rad2", "g_mse_mminus2", "folded_angle_bias_rad", "g_bias_mminus1"]
        methods = {name: {key: [i, 2*i] for key in metrics} for i, name in enumerate(names, 1)}
        result = dict(sweep="range", range_km=[5, 100], methods=methods, crlb=np.ones((4, 2)),
                      bias_theory_2019=np.ones((3, 2, 2)), frames_per_point=4, original_frames_per_point=2000)
        with tempfile.TemporaryDirectory() as tmp, patch("matplotlib.figure.Figure.savefig",
                                                         autospec=True) as save:
            plot_sweep(result, Path(tmp))
        pdfs = {path.stem: fig for (fig, path), _ in save.call_args_list if path.suffix == ".pdf"}
        self.assertEqual(set(pdfs), {"mpr_mse_range", "mpr_bias_range"})
        for fig in pdfs.values():
            self.assertEqual(len(fig.axes), 2)
            for ax in fig.axes:
                series = {line.get_label(): line for line in ax.get_lines()}
                self.assertEqual(series["Chan–Ho (Cartesian)"].get_marker(), "+")
                self.assertIn("Neural", series)
        g_panel = pdfs["mpr_mse_range"].axes[1]
        np.testing.assert_allclose(g_panel.lines[3].get_ydata(), 10*np.log10([4., 8.]))
