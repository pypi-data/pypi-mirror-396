import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class WaveletKANLayer(nn.Module):
    """
    WaveletKANLayer
    
    Replaces the standard B-Splines of KANs with learnable Morlet Wavelets.
    
    Formula:
        phi(x) = w_base * SiLU(x) + Sum( w_i * Wavelet((x - mu_i) / scale_i) )
    """
    def __init__(self, in_features, out_features, num_wavelets=5, epsilon=1e-5):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.num_wavelets = num_wavelets
        self.epsilon = epsilon # Avoid division by zero

        # Base weight (like the residual connection in original KAN)
        self.base_weight = nn.Parameter(torch.Tensor(out_features, in_features))
        
        # Wavelet parameters: Weights, Translation (mu), Scale (s)
        # Shape: (out_features, in_features, num_wavelets)
        self.wavelet_weights = nn.Parameter(torch.Tensor(out_features, in_features, num_wavelets))
        self.mu = nn.Parameter(torch.Tensor(out_features, in_features, num_wavelets))
        self.scale = nn.Parameter(torch.Tensor(out_features, in_features, num_wavelets))

        self.reset_parameters()

    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.base_weight, a=math.sqrt(5))
        
        with torch.no_grad():
            nn.init.normal_(self.wavelet_weights, mean=0.0, std=0.1)
            nn.init.normal_(self.mu, mean=0.0, std=1.0)
            nn.init.normal_(self.scale, mean=1.0, std=0.1)

    def morlet_wavelet(self, x, mu, scale):
        """
        Computes the Morlet Wavelet:
        psi(t) = exp(-t^2 / 2) * cos(5t)
        where t = (x - mu) / scale
        """
        t = (x.unsqueeze(-1) - mu) / (scale + self.epsilon)
        envelope = torch.exp(-0.5 * t**2)
        oscillation = torch.cos(5.0 * t)
        return envelope * oscillation

    def forward(self, x):
        # x shape: (Batch, In_Features)
        
        # 1. Base Linear path (SiLU activation included as per KAN paper)
        # Output: (Batch, Out)
        base_out = F.linear(F.silu(x), self.base_weight)
        
        # 2. Wavelet path
        # x_expanded: (Batch, In, 1) to broadcast with wavelets
        # Wavelets: Sum over the 'num_wavelets' dimension
        # phi(x) shape: (Batch, Out, In)
        
        # We need to compute Morlet for every input-output pair
        # This implementation uses memory efficient broadcasting
        
        # Reshape x for broadcasting: (Batch, 1, In, 1)
        x_reshaped = x.view(x.shape[0], 1, x.shape[1], 1)
        
        # Calculate wavelets: (Batch, Out, In, Num_Wavelets)
        # We broadcast mu/scale: (Out, In, Num_Wavelets)
        t = (x_reshaped - self.mu) / (self.scale + self.epsilon)
        wavelet_val = torch.exp(-0.5 * t**2) * torch.cos(5.0 * t)
        
        # Weighted sum of wavelets: (Batch, Out, In)
        # Sum over the 'num_wavelets' dimension (dim=3)
        wavelet_weighted = (wavelet_val * self.wavelet_weights).sum(dim=-1)
        
        # Sum over the 'In' dimension to get final output per neuron
        # Output: (Batch, Out)
        wavelet_out = wavelet_weighted.sum(dim=-1)
        
        return base_out + wavelet_out