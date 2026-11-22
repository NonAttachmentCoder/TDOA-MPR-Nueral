import unittest
import numpy as np
from tdoa_mpr.covariance import (differencing_matrix, range_difference_covariance,
                                  effective_covariance)
from tdoa_mpr.physics import mpr_jacobians


class TestCovariance(unittest.TestCase):
    def test_shared_reference_is_correlated(self):
        D = differencing_matrix()
        np.testing.assert_allclose(D.sum(axis=1), 0.)
        Q = range_difference_covariance(np.eye(8) * 0.25)
        np.testing.assert_allclose(np.diag(Q), 0.5)
        self.assertAlmostEqual(Q[0, 1], 0.25)
        self.assertEqual(np.linalg.matrix_rank(Q), 7)

    def test_monte_carlo_and_time_scaling(self):
        rng = np.random.default_rng(10)
        sigmas = np.arange(1., 9.) / 10
        Q = np.diag(sigmas**2)
        expected = range_difference_covariance(Q)
        samples = rng.normal(size=(50000, 8)) * sigmas[None, :]
        D = differencing_matrix()
        actual = np.cov((samples @ D.T), rowvar=False)
        np.testing.assert_allclose(actual, expected, rtol=0.08, atol=0.015)
        c = 3e8
        np.testing.assert_allclose(range_difference_covariance(Q / c**2, propagation_speed=c), expected)

    def test_first_order_position_error(self):
        s = np.random.default_rng(2).normal(size=(8, 3)) * 20
        u = np.array([0.5, 0.2, 0.8]); u /= np.linalg.norm(u)
        J = mpr_jacobians(u, 1/300., s).ds
        C = effective_covariance(np.eye(7), J, np.eye(24) * 0.1)
        self.assertEqual(C.shape, (7, 7))
        self.assertTrue(np.linalg.eigvalsh(C).min() >= 1)
        # Position error from a common translation must vanish at exact far field.
        J0 = mpr_jacobians(u, 0., s).ds
        for k in range(3):
            shared = np.tile(np.eye(3)[k], 8)
            np.testing.assert_allclose(J0 @ shared, 0, atol=1e-11)


if __name__ == "__main__":
    unittest.main()
