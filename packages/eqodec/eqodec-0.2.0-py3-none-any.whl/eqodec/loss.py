import torch
import torch.nn as nn
import math

class CarbonAwareLoss(nn.Module):
    """
    Carbon-aware rate–distortion loss.

    L = λ_r * MSE + λ_b * BPP + λ_c * CarbonProxy
    """
    def __init__(
        self,
        lambda_recon: float = 1.0,
        lambda_rate: float = 0.0,
        lambda_carbon: float = 0.0,
        carbon_intensity: float = 0.4
    ):
        super().__init__()
        self.mse = nn.MSELoss()
        self.lambda_recon = lambda_recon
        self.lambda_rate = lambda_rate
        self.lambda_carbon = lambda_carbon
        self.carbon_intensity = carbon_intensity

    def forward(self, x_hat, x, latent=None):
        loss = 0.0
        metrics = {}

        # Reconstruction
        mse = self.mse(x_hat, x)
        loss += self.lambda_recon * mse
        metrics["mse"] = mse.detach()

        # Rate proxy
        if latent is not None and self.lambda_rate > 0:
            bpp = torch.mean(torch.log1p(torch.abs(latent))) / math.log(2)
            loss += self.lambda_rate * bpp
            metrics["bpp"] = bpp.detach()

        # Carbon proxy
        if latent is not None and self.lambda_carbon > 0:
            carbon = (
                torch.mean(torch.log1p(torch.abs(latent)))
                * self.carbon_intensity
            )
            loss += self.lambda_carbon * carbon
            metrics["carbon_proxy"] = carbon.detach()

        return loss, metrics