import torch
import torch.nn as nn
from .layers import BinaryLinear
from .ste import binarize_activation
from .config import cfg

class BinarySign(nn.Module):
    """Activation layer that binarizes inputs to -1 or +1."""
    def forward(self, x):
        return binarize_activation(x)

class Quantizer(nn.Module):
    """Simulates FPGA fixed-point arithmetic (e.g., Q8.8)."""
    def __init__(self, fractional_bits):
        super().__init__()
        self.scale = 2 ** fractional_bits

    def forward(self, x):
        if not cfg.SIMULATE_FIXED_POINT:
            return x
        return torch.round(x * self.scale) / self.scale

class BWNLayer(nn.Module):
    """
    A single BNN Layer: Linear -> Quant -> BN -> Act.
    The 'Dense' logic is handled in the Classifier's forward pass.
    """
    def __init__(self, in_features, out_features):
        super().__init__()
        self.linear = BinaryLinear(in_features, out_features)
        self.quant = Quantizer(cfg.FRACTIONAL_BITS)
        self.bn = nn.BatchNorm1d(out_features)
        
        if cfg.ACTIVATION_TYPE == "BinarySign":
            self.activation = BinarySign()
        else:
            act_class = getattr(nn, cfg.ACTIVATION_TYPE)
            self.activation = act_class(**cfg.ACTIVATION_PARAMS)

    def forward(self, x):
        x = self.linear(x)
        x = self.quant(x)
        x = self.bn(x)
        x = self.activation(x)
        return x

class BWNClassifier(nn.Module):
    def __init__(self):
        super(BWNClassifier, self).__init__()
        
        self.input_quantizer = Quantizer(cfg.FRACTIONAL_BITS)
        self.use_res = cfg.USE_RESIDUALS
        
        self.layers = nn.ModuleList()
        
        # Track the cumulative input size
        cumulative_size = cfg.INPUT_SIZE
        
        for h_size in cfg.HIDDEN_LAYERS:
            # Create the layer with the current cumulative size
            self.layers.append(BWNLayer(cumulative_size, h_size))
            
            if self.use_res:
                # In Dense mode, the next layer's input grows by the size of this layer
                cumulative_size += h_size
            else:
                # In standard mode, the next layer's input is just this layer's output
                cumulative_size = h_size
                
        # Final Output Layer
        self.output_layer = BinaryLinear(cumulative_size, cfg.OUTPUT_SIZE)

    def forward(self, x):
        # 1. Initial Quantization
        x = self.input_quantizer(x)
        
        if self.use_res:
            # --- DENSE RESIDUAL LOGIC ---
            # List to store all previous outputs (including raw input)
            features = [x]
            
            for layer in self.layers:
                # Concatenate all previous features along the feature dimension (dim=1)
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
        
        # 3. Final linear layer
        logits = self.output_layer(final_input)
        
        return logits.squeeze(-1)