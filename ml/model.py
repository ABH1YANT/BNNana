"""
model.py
Defines the BWNClassifier. The architecture is parameterized to allow 
quick sweeps of hidden layer sizes (8, 16, 32, 64).
"""

import torch
import torch.nn as nn
from .layers import BinaryLinear
from .ste import binarize_activation
from .config import cfg

class BinarySign(nn.Module):
    """
    Activation layer that binarizes inputs to -1 or +1.
    Uses the Straight-Through Estimator (STE) defined in ste.py.
    """
    def forward(self, x):
        return binarize_activation(x)

class Quantizer(nn.Module):
    """
    Simulates FPGA fixed-point arithmetic (e.g., Q8.8).
    Used to mirror the precision of the FPGA's accumulators and BatchNorm logic.
    """
    def __init__(self, fractional_bits):
        super().__init__()
        self.scale = 2 ** fractional_bits

    def forward(self, x):
        if not cfg.SIMULATE_FIXED_POINT:
            return x
        # Simulate rounding to fixed-point precision
        return torch.round(x * self.scale) / self.scale

class BWNClassifier(nn.Module):
    def __init__(self):
        super(BWNClassifier, self).__init__()
        
        layers = []
        in_features = cfg.INPUT_SIZE
        
        # 1. Input Quantizer (Simulate Q8.8 conversion of the 17 float features)
        self.input_quantizer = Quantizer(cfg.FRACTIONAL_BITS)
        
        # 2. Dynamically build hidden layers
        for h_size in cfg.HIDDEN_LAYERS:
            # Linear Layer with Binary Weights (sign(W))
            layers.append(BinaryLinear(in_features, h_size))
            
            # Hardware-Aware: Quantize the accumulation result before BatchNorm
            layers.append(Quantizer(cfg.FRACTIONAL_BITS))
            
            # BatchNorm (Crucial for centering data before the Sign function)
            layers.append(nn.BatchNorm1d(h_size))
            
            # Binary Activation (sign(x))
            if cfg.ACTIVATION_TYPE == "BinarySign":
                layers.append(BinarySign())
            else:
                # Fallback for standard activations (ReLU, Hardtanh)
                act_class = getattr(nn, cfg.ACTIVATION_TYPE)
                layers.append(act_class(**cfg.ACTIVATION_PARAMS))
            
            in_features = h_size
        
        self.hidden_stack = nn.Sequential(*layers)
        
        # 3. Final Output Layer
        # Input is ±1 (from last hidden layer), Weights are ±1.
        # Result is a logit; we threshold at 0 during inference.
        self.output_layer = BinaryLinear(in_features, cfg.OUTPUT_SIZE)

    def forward(self, x):
        # Quantize raw input features
        x = self.input_quantizer(x)
        
        # Pass through binarized hidden layers
        x = self.hidden_stack(x)
        
        # Final linear layer
        x = self.output_layer(x)
        
        return x.squeeze(-1)