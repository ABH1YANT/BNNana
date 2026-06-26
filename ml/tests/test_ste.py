"""
test_ste.py
Verifies that the Straight Through Estimator (STE) correctly binarizes 
weights in the forward pass and passes gradients in the backward pass.
"""

import torch
import unittest
import sys
import os

# Add parent directory to path to import ml modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ste import binarize_weights

class TestSTE(unittest.TestCase):
    def test_forward_binarization(self):
        """Weights should become exactly 1.0 or -1.0."""
        weights = torch.tensor([0.5, -0.2, 0.0, 1.5, -10.0], requires_grad=True)
        expected = torch.tensor([1.0, -1.0, 1.0, 1.0, -1.0])
        
        binary_w = binarize_weights(weights)
        self.assertTrue(torch.equal(binary_w, expected))

    def test_backward_identity(self):
        """Gradient should pass through as identity (1.0)."""
        weights = torch.tensor([0.5], requires_grad=True)
        binary_w = binarize_weights(weights)
        
        # Simulate a loss and backward pass
        loss = binary_w * 2  # d(loss)/d(binary_w) = 2
        loss.backward()
        
        # If STE works, d(loss)/d(weights) should also be 2
        self.assertEqual(weights.grad.item(), 2.0)

if __name__ == '__main__':
    unittest.main()