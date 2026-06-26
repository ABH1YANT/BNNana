"""
layers.py
Defines the BinaryLinear layer which uses binarized weights for the 
forward pass while maintaining full-precision weights for gradient updates.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from ste import binarize_weights

class BinaryLinear(nn.Module):
    """
    A custom Linear layer compatible with FPGA-based BWN.
    Weights are binarized to {-1, 1} during the forward pass.
    """
    def __init__(self, in_features, out_features, bias=True):
        super(BinaryLinear, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        # High-precision weight parameter (used for accumulation during training)
        self.weight = nn.Parameter(torch.Tensor(out_features, in_features))
        
        if bias:
            self.bias = nn.Parameter(torch.Tensor(out_features))
        else:
            self.register_parameter('bias', None)
            
        self.reset_parameters()

    def reset_parameters(self):
        # Initialize weights using Xavier/Glorot initialization
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            nn.init.zeros_(self.bias)

    def forward(self, x):
        # 1. Binarize the weights using the STE
        binary_w = binarize_weights(self.weight)
        
        # 2. Perform standard linear operation: y = xW^T + b
        # On the FPGA, this will be implemented as Add/Subtract logic.
        return F.linear(x, binary_w, self.bias)

import math # Added for reset_parameters