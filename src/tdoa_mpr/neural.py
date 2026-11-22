"""Candidate neural-first dynamic TDOA physics-query estimator.

Unlike a classical MPR solver, this network does not receive an analytic
localization initial value, call a least-squares step, or apply a final
analytical solution. Its learned global representation is updated using
the *exact* near/far range-difference forward map at its own previous
estimates. The architecture is exploratory, not a verified paper result.
"""
import torch
from torch import nn
import torch.nn.functional as F


def torch_range_differences(u, g, stations):
    """Batch exact analytic continuation with reference station 0.

    u [B,3], g [B], stations [B,8,3], result [B,7] in meters.
    """
    si, s0 = stations[:, 1:, :], stations[:, :1, :]
    x_i = u[:, None, :] - g[:, None, None] * si
    x_0 = u[:, None, :] - g[:, None, None] * s0
    ai = torch.linalg.vector_norm(x_i, dim=-1)
    a0 = torch.linalg.vector_norm(x_0, dim=-1)
    ds = si - s0
    dq = (si.square().sum(-1) - s0.square().sum(-1))
    numerator = -2.0 * (ds * u[:, None, :]).sum(-1) + g[:, None] * dq
    return numerator / (ai + a0).clamp_min(1e-9)


class DynamicTDOAMPR(nn.Module):
    """One shared set of parameters for all ranges and station geometries."""

    def __init__(self, hidden=96, iterations=3, radial_limit=4.0,
                 use_physical_query=True, use_full_qr=True):
        super().__init__()
        if iterations < 1:
            raise ValueError("iterations must be positive")
        self.hidden = int(hidden)
        self.iterations = int(iterations)
        self.radial_limit = float(radial_limit)
        self.use_physical_query = bool(use_physical_query)
        self.use_full_qr = bool(use_full_qr)
        # Per-station: y, prediction, difference, standardized discrepancy,
        # position(3), baseline(3), site pos. uncertainty(3), Qr row(7),
        # state direction(3), scaled g(1), predicted bearing(3) = 27.
        self.station_encoder = nn.Sequential(
            nn.Linear(27, hidden), nn.SiLU(),
            nn.Linear(hidden, hidden), nn.SiLU())
        # Full Qr correlation(49), receiver arrival precisions(7),
        # full reported station Qs(576), log aperture(1) = 633.
        extra_features = 49 + 7 + 576 + 1
        self.global_encoder = nn.Sequential(
            nn.Linear(2 * hidden + extra_features + 4, hidden),
            nn.SiLU(), nn.Linear(hidden, hidden), nn.SiLU())
        self.memory = nn.GRUCell(hidden, hidden)
        self.direction_head = nn.Linear(hidden, 3)
        self.range_head = nn.Linear(hidden, 1)

    def forward(self, y, stations, qr, qs):
        if y.ndim != 2 or y.shape[1] != 7:
            raise ValueError("y must be [B,7]")
        b = y.shape[0]
        if stations.shape != (b, 8, 3) or qr.shape != (b, 7, 7) or qs.shape != (b, 24, 24):
            raise ValueError("expected stations [B,8,3], Qr [B,7,7], Qs [B,24,24]")
        # Scale every frame by its reported station-network RMS aperture.
        aperture = torch.sqrt((stations - stations.mean(dim=1, keepdim=True)).square()
                             .sum(-1).mean(-1)).clamp_min(1.)
        l = aperture[:, None]
        pos = stations / l[:, :, None]
        baseline = (stations[:, 1:, :] - stations[:, :1, :]) / l[:, :, None]
        diag_qr = torch.diagonal(qr, dim1=-2, dim2=-1).clamp_min(1e-14)
        sigmas = torch.sqrt(diag_qr)
        corr = qr / (sigmas[:, :, None] * sigmas[:, None, :])
        if not self.use_full_qr:
            corr = torch.diag_embed(torch.ones_like(sigmas))
        sig_norm = (sigmas / l).clamp_min(1e-12)
        qs_scaled = qs / (l[:, :, None] * l[:, None, :])
        site_sigmas = torch.sqrt(torch.diagonal(qs, dim1=-2, dim2=-1)
                                 .clamp_min(0)).reshape(b, 8, 3) / l[:, :, None]
        extras = torch.cat([corr.reshape(b, -1), sig_norm.log(),
                            qs_scaled.reshape(b, -1), aperture.log()[:, None]], dim=-1)
        hidden_state = y.new_zeros((b, self.hidden))
        direction = F.normalize(torch.tensor([1.0, 0.0, 0.0], device=y.device,
                                              dtype=y.dtype).expand(b, -1), dim=-1)
        g_scaled = y.new_zeros(b)
        states = []
        for step in range(self.iterations):
            g = g_scaled / aperture
            prediction = (torch_range_differences(direction, g, stations)
                          if step and self.use_physical_query else torch.zeros_like(y))
            residual = y - prediction
            source_vectors = direction[:, None, :] - g[:, None, None] * stations[:, 1:, :]
            bearings = (F.normalize(source_vectors, dim=-1) if self.use_physical_query
                        else direction[:, None, :].expand(-1, 7, -1))
            features = torch.cat([
                (y / l)[:, :, None],
                (prediction / l)[:, :, None],
                (residual / l)[:, :, None],
                torch.asinh(residual / sigmas)[:, :, None],
                pos[:, 1:, :], baseline,
                site_sigmas[:, 1:, :], corr,
                direction[:, None, :].expand(-1, 7, -1),
                g_scaled[:, None, None].expand(-1, 7, -1),
                bearings
            ], dim=-1)
            nodes = self.station_encoder(features)
            pooled = torch.cat([nodes.mean(dim=1), nodes.amax(dim=1)], dim=-1)
            query = torch.cat([pooled, extras, direction, g_scaled[:, None]], dim=-1)
            hidden_state = self.memory(self.global_encoder(query), hidden_state)
            direction = F.normalize(self.direction_head(hidden_state), dim=-1, eps=1e-8)
            g_scaled = self.radial_limit * torch.tanh(self.range_head(hidden_state).squeeze(-1))
            states.append((direction, g_scaled / aperture))
        return {"u": direction, "g": g_scaled / aperture, "states": states}


def joint_point_loss(outputs, u_true, g_true, stations,
                     radial_weight=0.4, auxiliary_weight=0.35):
    """Stable sphere chord and aperture-scaled inverse-range supervision.

    The auxiliary stages share all model weights; they are not independently
    trained solver outputs. This is an editable experimental training choice.
    """
    aperture = torch.sqrt((stations - stations.mean(dim=1, keepdim=True))
                         .square().sum(-1).mean(-1)).clamp_min(1.)
    def risk(u, g):
        angle_term = (1. - (u * u_true).sum(-1).clamp(-1., 1.)).mean()
        radial_term = ((g - g_true) * aperture).square().mean()
        return angle_term + radial_weight * radial_term
    final = risk(outputs["u"], outputs["g"])
    if len(outputs["states"]) <= 1:
        return final
    intermediate = sum(risk(u, g) for u, g in outputs["states"][:-1])
    return final + auxiliary_weight * intermediate / (len(outputs["states"]) - 1)


@torch.no_grad()
def predict_numpy(model, y, stations, qr, qs):
    """Numpy inference wrapper for a single frame, preserving negative g."""
    import numpy as np
    model.eval()
    device = next(model.parameters()).device
    tensors = [torch.as_tensor(np.asarray(x)[None], dtype=torch.float32, device=device)
               for x in (y, stations, qr, qs)]
    out = model(*tensors)
    return out["u"][0].cpu().numpy(), float(out["g"][0].cpu())
