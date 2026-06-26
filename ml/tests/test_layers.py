"""
test_layers.py
Verifies the BinaryLinear layer behavior.
"""

import torch
import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from layers import BinaryLinear

class TestLayers(unittest.TestCase):
    def test_layer_output_shape(self):
        """Verify output dimensions match expectations."""
        batch_size = 8
        in_feats = 17
        out_feats = 16
        
        layer = BinaryLinear(in_feats, out_feats)
        input_data = torch.randn(batch_size, in_feats)
        output = layer(input_data)
        
        self.assertEqual(output.shape, (batch_size, out_feats))

    def test_weight_persistence(self):
        """Verify that underlying weights remain full-precision (not just 1 or -1)."""
        layer = BinaryLinear(10, 5)
        # Check if any weights are not 1 or -1 (they should be random floats initially)
        weights = layer.weight.data
        is_binary = torch.all((weights == 1.0) | (weights == -1.0))
        self.assertFalse(is_binary.item(), "Underlying weights should be full-precision floats.")

if __name__ == '__main__':
    unittest.main()