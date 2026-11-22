import unittest
import numpy as np
from tdoa_mpr.simulation import SimulationConfig, sample_frame, sample_batch
from tdoa_mpr.covariance import range_difference_covariance


class TestSimulation(unittest.TestCase):
    def test_repeatable_and_dimensions(self):
        cfg = SimulationConfig()
        a = sample_batch(np.random.default_rng(20), 4, cfg)
        b = sample_batch(np.random.default_rng(20), 4, cfg)
        for key in a:
            np.testing.assert_array_equal(a[key], b[key])
        self.assertEqual(a["y"].shape, (4, 7))
        self.assertEqual(a["stations"].shape, (4, 8, 3))
        self.assertEqual(a["qs"].shape, (4, 24, 24))
        self.assertTrue(np.all(a["g"] > 0))
        self.assertTrue(np.all(np.linalg.eigvalsh(a["qr"]) > 0))

    def test_reference_noise_shared_by_differences(self):
        cfg = SimulationConfig()
        frame = sample_frame(np.random.default_rng(25), cfg)
        e = frame["arrival_error"]
        np.testing.assert_allclose(frame["y"] - frame["clean_y"], e[1:] - e[0])
        self.assertTrue(np.all(frame["qr"][~np.eye(7, dtype=bool)] > 0))

    def test_zero_contamination_clean_contract(self):
        cfg = SimulationConfig(outlier_probability=0., positive_delay_bias_probability=0.)
        one = sample_frame(np.random.default_rng(21), cfg)
        self.assertGreater(np.linalg.norm(one["y"] - one["clean_y"]), 0)


if __name__ == "__main__":
    unittest.main()
