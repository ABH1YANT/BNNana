"""
layers.py
Defines the BinaryLinear layer which uses binarized weights for the 
forward pass while maintaining full-precision weights for gradient updates.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from .ste import binarize_weights
from .config import cfg

class BinaryLinear(nn.Module):
    """
    A BNN-optimized Linear layer.
    
    FPGA Mapping:
    - Layer 1: Input is float, Weight is ±1. 
      Logic: Accumulator += (weight > 0) ? input : -input.
    - Layer 2+: Input is ±1, Weight is ±1.
      Logic: XNOR + Popcount.
    """
    def __init__(self, in_features, out_features, bias=True):
        super(BinaryLinear, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        # High-precision latent weights used for gradient updates
        self.weight = nn.Parameter(torch.Tensor(out_features, in_features))
        
        if bias:
            # Note: In many BNNs, bias is omitted if BatchNorm follows,
            # but we keep it here for modularity.
            self.bias = nn.Parameter(torch.Tensor(out_features))
        else:
            self.register_parameter('bias', None)
            
        self.reset_parameters()

    def reset_parameters(self):
        # Kaiming initialization is standard for BNNs to keep 
        # latent weights in a range where they can flip signs easily.
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            nn.init.zeros_(self.bias)

    def forward(self, x):
        # 1. Binarize weights to {-1, 1} using STE
        # This ensures that during the forward pass, the FPGA logic is mirrored.
        bw = binarize_weights(self.weight)
        
        # 2. Perform Linear Operation
        # PyTorch's F.linear(x, bw) handles both:
        # - Float (input) * Binary (weight) -> Layer 1
        # - Binary (input) * Binary (weight) -> Layer 2+ (XNOR-Popcount equivalent)
        return F.linear(x, bw, self.bias)

    def __repr__(self):
        return f"BinaryLinear(in={self.in_features}, out={self.out_features}, bias={self.bias is not None})"