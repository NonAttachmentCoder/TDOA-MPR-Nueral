import unittest
import numpy as np
from tdoa_mpr.physics import range_differences, mpr_jacobians, tangent_basis, local_information


class TestMPRPhysics(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(17)
        self.stations = self.rng.normal(size=(8, 3)) * 23.0
        self.stations[0] = np.array([3., -5., 1.])
        self.u = np.array([0.55, -0.3, 0.8])
        self.u /= np.linalg.norm(self.u)

    def test_cartesian_equivalence(self):
        for r in (30., 100., 400., 10000., 80000.):
            p = r * self.u
            expected = np.linalg.norm(p - self.stations[1:], axis=1) - np.linalg.norm(p - self.stations[0])
            np.testing.assert_allclose(range_differences(self.u, 1/r, self.stations),
                                       expected, atol=2e-10, rtol=3e-9)

    def test_exact_plane_wave_and_very_small_g(self):
        target = -(self.stations[1:] - self.stations[0]) @ self.u
        np.testing.assert_allclose(range_differences(self.u, 0., self.stations), target, atol=1e-12)
        np.testing.assert_allclose(range_differences(self.u, 1e-13, self.stations), target, atol=1e-8)

    def test_angle_and_range_jacobian_including_exact_zero(self):
        for g in (0., 1/100., 1/3000.):
            j = mpr_jacobians(self.u, g, self.stations)
            E = tangent_basis(self.u)
            self.assertLess(np.linalg.norm(E.T @ E - np.eye(2)), 1e-12)
            eps = 1e-7
            for k in range(2):
                up = self.u + eps * E[:, k]
                um = self.u - eps * E[:, k]
                fd = (range_differences(up, g, self.stations) -
                      range_differences(um, g, self.stations)) / (2 * eps)
                np.testing.assert_allclose(j.du @ E[:, k], fd, atol=3e-6, rtol=3e-5)
            # g finite difference sensitivity is O(aperture^2).
            eps_g = 1e-8
            fd = (range_differences(self.u, g + eps_g, self.stations) -
                  range_differences(self.u, g - eps_g, self.stations)) / (2 * eps_g)
            np.testing.assert_allclose(j.dg, fd, atol=1e-4, rtol=1e-5)

    def test_sensor_jacobian(self):
        g = 1/300.
        j = mpr_jacobians(self.u, g, self.stations)
        eps = 1e-6
        for i in (0, 1, 7):
            for k in range(3):
                sp = self.stations.copy()
                sm = self.stations.copy()
                sp[i, k] += eps
                sm[i, k] -= eps
                fd = (range_differences(self.u, g, sp) -
                      range_differences(self.u, g, sm)) / (2 * eps)
                np.testing.assert_allclose(j.ds[:, 3*i+k], fd, atol=4e-7, rtol=1e-5)

    def test_ambient_jacobian_includes_direction_normalization(self):
        for scale in (1., 2.5):
            u = scale * self.u
            for g in (0., -1/100., 1/100.):
                j = mpr_jacobians(u, g, self.stations)
                eps = 1e-7
                fd = np.column_stack([
                    (range_differences(u + eps * axis, g, self.stations) -
                     range_differences(u - eps * axis, g, self.stations)) / (2 * eps)
                    for axis in np.eye(3)])
                np.testing.assert_allclose(j.du, fd, atol=3e-6, rtol=3e-5)
                np.testing.assert_allclose(j.du @ u, 0., atol=1e-11)

    def test_reference_change(self):
        # Exact all-pairs consistency; differences must agree through a receiver-level vector.
        h0 = range_differences(self.u, 1/100., self.stations, ref=0)
        full = np.r_[0., h0]
        for ref in (1, 4, 7):
            expected = full[np.arange(8) != ref] - full[ref]
            np.testing.assert_allclose(range_differences(self.u, 1/100., self.stations, ref),
                                       expected, atol=1e-11)

    def test_bound(self):
        qr = np.eye(7) * 0.1
        b = local_information(self.u, 1/500., self.stations, qr)
        self.assertTrue(b.valid)
        np.testing.assert_allclose(b.covariance @ b.information, np.eye(3), atol=1e-8)
        self.assertTrue(b.direction_trace > 0 and b.inverse_range_variance > 0)
        scaled = local_information(2.5 * self.u, 1/500., self.stations, qr)
        np.testing.assert_allclose(scaled.information, b.information, rtol=1e-12)


if __name__ == "__main__":
    unittest.main()
