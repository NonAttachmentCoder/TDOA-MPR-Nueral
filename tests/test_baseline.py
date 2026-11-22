import unittest
import numpy as np
from tdoa_mpr.baseline import solve_mpr_wls
from tdoa_mpr.physics import range_differences


class TestNumericalWLS(unittest.TestCase):
    def test_one_noiseless_case(self):
        rng = np.random.default_rng(19)
        s = rng.normal(size=(8, 3)) * 30
        s[0] = 0
        u = np.array([0.8, 0.4, 0.3])
        u /= np.linalg.norm(u)
        g = 1/300
        y = range_differences(u, g, s)
        solved = solve_mpr_wls(y, s, np.eye(7) * 0.25, max_nfev=100)
        self.assertTrue(solved.success, solved.message)
        self.assertLess(np.linalg.norm(y - range_differences(solved.u, solved.g, s)), 2e-3)


if __name__ == "__main__":
    unittest.main()
