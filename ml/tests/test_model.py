"""
test_model.py
Verifies the full BWNClassifier architecture.
"""

import torch
import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model import BWNClassifier
from config import cfg

class TestModel(unittest.TestCase):
    def setUp(self):
        self.model = BWNClassifier(cfg.INPUT_SIZE, cfg.HIDDEN_SIZE, cfg.OUTPUT_SIZE)

    def test_forward_pass(self):
        """Verify a single forward pass with dummy data."""
        # 17 features as input
        dummy_input = torch.randn(1, cfg.INPUT_SIZE)
        output = self.model(dummy_input)
        
        # Output should be a single logit
        self.assertEqual(output.shape, (1, 1))

    def test_batch_norm_exists(self):
        """Ensure BatchNorm is present for the hardware thresholding logic."""
        has_bn = any(isinstance(layer, torch.nn.BatchNorm1d) for layer in self.model.modules())
        self.assertTrue(has_bn, "Model must include BatchNorm for FPGA threshold fusion.")

if __name__ == '__main__':
    unittest.main()