"""
model.py
Defines the BWNClassifier. The architecture is parameterized to allow 
quick sweeps of hidden layer sizes (8, 16, 32, 64).
"""

import torch
import torch.nn as nn
from .layers import BinaryLinear
from .config import cfg

class BWNClassifier(nn.Module):
    def __init__(self):
        super(BWNClassifier, self).__init__()
        
        layers = []
        in_features = cfg.INPUT_SIZE
        
        # Dynamically build hidden layers
        for h_size in cfg.HIDDEN_LAYERS:
            layers.append(BinaryLinear(in_features, h_size))
            layers.append(nn.BatchNorm1d(h_size))
            
            # Resolve activation function from string
            act_class = getattr(nn, cfg.ACTIVATION_TYPE)
            layers.append(act_class(**cfg.ACTIVATION_PARAMS))
            
            in_features = h_size
        
        self.hidden_stack = nn.Sequential(*layers)
        
        # Final Output Layer
        self.output_layer = BinaryLinear(in_features, cfg.OUTPUT_SIZE)

    def forward(self, x):
        x = self.hidden_stack(x)
        x = self.output_layer(x)
        return x.squeeze(-1)