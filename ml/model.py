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
    """Simulates Q1.8 fixed-point arithmetic for the input stage."""
    def __init__(self, fractional_bits=8):
        super().__init__()
        self.scale = 2 ** fractional_bits

    def forward(self, x):
        if not cfg.SIMULATE_FIXED_POINT:
            return x
        x = torch.clamp(x, -1.0, 1.0 - (1.0 / self.scale))
        return torch.round(x * self.scale) / self.scale

class BNNLayer(nn.Module):
    """Standard BNN Layer: Linear -> BatchNorm -> Activation."""
    def __init__(self, in_features, out_features):
        super().__init__()
        self.linear = BinaryLinear(in_features, out_features)
        self.bn = nn.BatchNorm1d(out_features)
        
        if cfg.ACTIVATION_TYPE == "BinarySign":
            self.activation = BinarySign()
        else:
            act_class = getattr(nn, cfg.ACTIVATION_TYPE)
            self.activation = act_class(**cfg.ACTIVATION_PARAMS)

    def forward(self, x):
        return self.activation(self.bn(self.linear(x)))

class BNNClassifier(nn.Module):
    def __init__(self):
        super(BNNClassifier, self).__init__()
        
        self.input_quantizer = Quantizer(fractional_bits=8)
        self.use_res = cfg.USE_RESIDUALS
        h_sizes = cfg.HIDDEN_LAYERS
        
        self.layers = nn.ModuleList()
        
        # --- Layer 1: Input (Q1.8) -> Binary ---
        # This layer always takes the raw features
        self.layers.append(BNNLayer(cfg.INPUT_SIZE, h_sizes[0]))
        
        if len(h_sizes) > 1:
            # --- Layer 2 and Beyond ---
            # We track the size of the concatenated binary features
            # Starting with just the output of Layer 1
            current_cumulative_size = h_sizes[0]
            
            for i in range(1, len(h_sizes)):
                # Each layer takes either the previous layer OR the concatenation of all previous
                self.layers.append(BNNLayer(current_cumulative_size, h_sizes[i]))
                
                if self.use_res:
                    # If residuals are on, the next layer's input size grows
                    current_cumulative_size += h_sizes[i]
                else:
                    # If residuals are off, the next layer's input is just the previous output
                    current_cumulative_size = h_sizes[i]
            
            self.final_in_size = current_cumulative_size
        else:
            self.final_in_size = h_sizes[0]

        # Final Output Layer
        self.output_layer = BinaryLinear(self.final_in_size, cfg.OUTPUT_SIZE)

    def forward(self, x):
        # 1. Quantize raw input features to Q1.8
        x = self.input_quantizer(x)
        
        # 2. Layer 1 (Consumes Q1.8, produces first Binary output)
        out = self.layers[0](x)
        
        if len(self.layers) == 1:
            return self.output_layer(out).squeeze(-1)

        if not self.use_res:
            # --- STANDARD SEQUENTIAL FLOW ---
            for i in range(1, len(self.layers)):
                out = self.layers[i](out)
            final_input = out
        else:
            # --- DENSE CONCATENATION FLOW ---
            # binary_history starts with Layer 1 output. 
            # Raw input 'x' is NOT included here.
            binary_history = [out]
            
            for i in range(1, len(self.layers)):
                # Concatenate all previous binary outputs
                dense_input = torch.cat(binary_history, dim=1)
                out = self.layers[i](dense_input)
                binary_history.append(out)
            
            # Final layer receives the concatenation of all hidden binary outputs
            final_input = torch.cat(binary_history, dim=1)

        # 3. Final linear layer
        logits = self.output_layer(final_input)
        return logits.squeeze(-1)