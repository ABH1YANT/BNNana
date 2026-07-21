"""
ste.py
Implements the Straight Through Estimator (STE) for weight binarization.
This allows gradients to flow through the non-differentiable sign() function.
"""

import torch

class BinaryWeightSTE(torch.autograd.Function):
    """
    Straight Through Estimator with Gradient Clipping.
    Forward: sign(w)
    Backward: Identity if |w| <= 1, else 0.
    """
    @staticmethod
    def forward(ctx, input_weights):
        # Save input for the clipping logic in backward
        ctx.save_for_backward(input_weights)
        
        binary_weights = torch.sign(input_weights)
        # Ensure binary state is strictly {-1, 1}
        binary_weights[binary_weights == 0] = 1
        return binary_weights

    @staticmethod
    def backward(ctx, grad_output):
        input_weights, = ctx.saved_tensors
        grad_input = grad_output.clone()
        
        # Gradient Clipping: If the weight is too far outside the [-1, 1] range,
        # we stop updating it. This is standard for stable BNN training.
        grad_input[input_weights.abs() > 1.0] = 0
        
        return grad_input

def binarize_weights(w):
    return BinaryWeightSTE.apply(w)