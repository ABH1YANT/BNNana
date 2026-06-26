"""
model.py
Defines the BWNClassifier. The architecture is parameterized to allow 
quick sweeps of hidden layer sizes (8, 16, 32, 64).
"""

import torch
import torch.nn as nn
from layers import BinaryLinear

class BWNClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(BWNClassifier, self).__init__()
        
        # Hidden Layer: Binary Weights, Full-Precision Inputs
        self.hidden = BinaryLinear(input_size, hidden_size)
        
        # BatchNorm: Crucial for centering data before thresholding.
        # This will be fused into the hardware threshold later.
        self.bn = nn.BatchNorm1d(hidden_size)
        
        # Activation: Using ReLU for training stability. 
        # On FPGA, this becomes the "Threshold Comparison".
        self.relu = nn.ReLU()
        
        # Output Layer: Binary Weights
        self.output = BinaryLinear(hidden_size, output_size)
        
        # Note: No Sigmoid here because BCEWithLogitsLoss is more numerically stable.

    def forward(self, x):
        # Input (17) -> Hidden (Binary Weights)
        x = self.hidden(x)
        
        # BatchNorm + Activation
        x = self.bn(x)
        x = self.relu(x)
        
        # Hidden -> Output (Binary Weights)
        x = self.output(x)
        return x