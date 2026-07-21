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

class BinaryLinear(nn.Module):
    def __init__(self, in_features, out_features, bias=True):
        super(BinaryLinear, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        self.weight = nn.Parameter(torch.Tensor(out_features, in_features))
        if bias:
            self.bias = nn.Parameter(torch.Tensor(out_features))
        else:
            self.register_parameter('bias', None)
            
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            nn.init.zeros_(self.bias)

    def forward(self, x):
        binary_w = binarize_weights(self.weight)
        return F.linear(x, binary_w, self.bias)