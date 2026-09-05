"""
layers.py
Defines the BinaryLinear layer for Binarized Neural Networks (BNN).
Uses binarized weights (+1, -1) for the forward pass while maintaining 
full-precision latent weights for gradient updates.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from .ste import binarize_weights
from .config import cfg

class BinaryLinear(nn.Module):
    """
    A BNN-optimized Linear layer without bias.
    
    Hardware / FPGA Mapping:
    - Layer 1: Input is Q1.8 fixed-point, Weight is ±1. 
      Logic: Accumulator += (weight > 0) ? input : -input.
    - Layer 2+: Input is ±1 (Binary), Weight is ±1 (Binary).
      Logic: XNOR + Popcount.
    """
    def __init__(self, in_features, out_features):
        super(BinaryLinear, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        # High-precision latent weights used for gradient updates.
        # These are binarized to ±1 during the forward pass.
        self.weight = nn.Parameter(torch.Tensor(out_features, in_features))
        
        # Bias is removed to simplify the hardware datapath and 
        # because BatchNorm handles the learnable shift (beta).
        self.reset_parameters()

    def reset_parameters(self):
        # Kaiming initialization keeps latent weights in a range 
        # where they can easily flip signs across the zero-threshold.
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))

    def forward(self, x):
        # 1. Binarize latent weights to {-1, 1} using the STE.
        # This ensures the PC simulation matches the FPGA's 1-bit weight registers.
        bw = binarize_weights(self.weight)
        
        # 2. Perform Linear Operation (Wx).
        # - If x is Q1.8 (Layer 1), this is a signed accumulation.
        # - If x is ±1 (Layer 2+), this is mathematically equivalent to XNOR-Popcount.
        return F.linear(x, bw, None)

    def __repr__(self):
        return f"BinaryLinear(in={self.in_features}, out={self.out_features}, bias=False)"