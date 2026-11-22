import unittest
import numpy as np
from tdoa_mpr.simulation import sample_batch
from tdoa_mpr.physics import range_differences

try:
    import torch
    from tdoa_mpr.neural import DynamicTDOAMPR, torch_range_differences, joint_point_loss
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


@unittest.skipUnless(TORCH_AVAILABLE, "PyTorch optional dependency unavailable")
class TestNeural(unittest.TestCase):
    def test_physics_compatibility_and_zero_limit(self):
        rng = np.random.default_rng(44)
        s = rng.normal(size=(2, 8, 3)) * 20
        u = rng.normal(size=(2, 3))
        u /= np.linalg.norm(u, axis=1, keepdims=True)
        for g in (0., -1/600., 1/300.):
            expected = np.stack([range_differences(u[i], g, s[i]) for i in range(2)])
            got = torch_range_differences(
                torch.tensor(u, dtype=torch.float64),
                torch.tensor([g, g], dtype=torch.float64),
                torch.tensor(s, dtype=torch.float64)).numpy()
            np.testing.assert_allclose(got, expected, atol=1e-10, rtol=1e-9)

    def test_controls_use_same_capacity(self):
        base = DynamicTDOAMPR(hidden=16, iterations=2)
        ctrl = DynamicTDOAMPR(hidden=16, iterations=2,
                              use_physical_query=False, use_full_qr=False)
        self.assertEqual(sum(p.numel() for p in base.parameters()),
                         sum(p.numel() for p in ctrl.parameters()))
        frames = sample_batch(np.random.default_rng(12), 2)
        inputs = [torch.as_tensor(frames[k], dtype=torch.float32)
                  for k in ("y", "stations", "qr", "qs")]
        out = ctrl(*inputs)
        self.assertTrue(torch.isfinite(out["u"]).all())
        self.assertTrue(torch.isfinite(out["g"]).all())

    def test_forward_backward(self):
        torch.manual_seed(1)
        frames = sample_batch(np.random.default_rng(9), 3)
        def t(k):
            return torch.as_tensor(frames[k], dtype=torch.float32)
        model = DynamicTDOAMPR(hidden=24, iterations=2)
        out = model(t("y"), t("stations"), t("qr"), t("qs"))
        self.assertEqual(out["u"].shape, (3, 3))
        self.assertEqual(out["g"].shape, (3,))
        self.assertTrue(torch.isfinite(out["u"]).all())
        self.assertTrue(torch.isfinite(out["g"]).all())
        loss = joint_point_loss(out, t("u"), t("g"), t("stations"))
        loss.backward()
        self.assertTrue(torch.isfinite(loss).item())
        self.assertTrue(any(p.grad is not None for p in model.parameters()))


if __name__ == "__main__":
    unittest.main()
