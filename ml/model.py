"""
model.py
Defines the Binarized Neural Network (BNN) architecture.
Features:
- Hardware-aware Quantization (Fixed-point simulation)
- Dense Residual Connections (Concatenation)
- BinarySign Activation for 1-bit inference
"""

import torch
import torch.nn as nn
from .layers import BinaryLinear
from .ste import binarize_activation
from .config import cfg

class BinarySign(nn.Module):
    """
    Activation layer that binarizes inputs to -1 or +1.
    Uses the Straight-Through Estimator (STE) during backpropagation.
    """
    def forward(self, x):
        return binarize_activation(x)

class Quantizer(nn.Module):
    """
    Simulates FPGA/MCU fixed-point arithmetic (e.g., Q8.8).
    Ensures that the model trained on PC matches hardware behavior.
    """
    def __init__(self, fractional_bits):
        super().__init__()
        self.scale = 2 ** fractional_bits

    def forward(self, x):
        if not cfg.SIMULATE_FIXED_POINT:
            return x
        # Rounding to the nearest fixed-point value
        return torch.round(x * self.scale) / self.scale

class BWNLayer(nn.Module):
    """
    A single BNN Layer: Linear -> Quantization -> BatchNormalization -> Activation.
    BatchNormalization is essential to center data before binarization.
    """
    def __init__(self, in_features, out_features):
        super().__init__()
        # BinaryLinear uses binarized weights (-1, +1) in the forward pass
        self.linear = BinaryLinear(in_features, out_features)
        self.quant = Quantizer(cfg.FRACTIONAL_BITS)
        self.bn = nn.BatchNorm1d(out_features)
        
        if cfg.ACTIVATION_TYPE == "BinarySign":
            self.activation = BinarySign()
        else:
            # Fallback for standard activations (ReLU, etc.)
            act_class = getattr(nn, cfg.ACTIVATION_TYPE)
            self.activation = act_class(**cfg.ACTIVATION_PARAMS)

    def forward(self, x):
        x = self.linear(x)
        x = self.quant(x)
        x = self.bn(x)
        x = self.activation(x)
        return x

class BWNClassifier(nn.Module):
    """
    The main BNN Classifier.
    Implements Dense Residual Logic (Concatenation) to preserve 
    feature information across 1-bit layers.
    """
    def __init__(self):
        super(BWNClassifier, self).__init__()
        
        self.input_quantizer = Quantizer(cfg.FRACTIONAL_BITS)
        self.use_res = cfg.USE_RESIDUALS
        
        self.layers = nn.ModuleList()
        
        # Track the cumulative input size for Dense connections
        # Starts with the 16 features from Log-Mix preprocessing
        cumulative_size = cfg.INPUT_SIZE
        
        # Build hidden layers based on config [512, 256, 128]
        for h_size in cfg.HIDDEN_LAYERS:
            self.layers.append(BWNLayer(cumulative_size, h_size))
            
            if self.use_res:
                # DENSE MODE: Next layer input grows by the size of this layer
                cumulative_size += h_size
            else:
                # STANDARD MODE: Next layer input = current layer output
                cumulative_size = h_size
                
        # Final Output Layer (Produces Logits)
        self.output_layer = BinaryLinear(cumulative_size, cfg.OUTPUT_SIZE)

    def forward(self, x):
        # 1. Initial Hardware-Aware Quantization
        x = self.input_quantizer(x)
        
        if self.use_res:
            # --- DENSE RESIDUAL LOGIC (Concatenation) ---
            # Stores all previous outputs to prevent information loss
            features = [x]
            
            for layer in self.layers:
                # Concatenate all previous features along the feature dimension
                current_input = torch.cat(features, dim=1)
                out = layer(current_input)
                features.append(out)
            
            # Final layer receives the concatenation of EVERYTHING
            final_input = torch.cat(features, dim=1)
            
        else:
            # --- STANDARD FEED-FORWARD LOGIC ---
            out = x
            for layer in self.layers:
                out = layer(out)
            final_input = out
        
        # 3. Final linear layer to produce classification logits
        logits = self.output_layer(final_input)
        
        return logits.squeeze(-1)