"""
ste.py
Implements the Straight Through Estimator (STE) for weight binarization.
This allows gradients to flow through the non-differentiable sign() function.
"""

import torch

class BinaryWeightSTE(torch.autograd.Function):
    """
    Custom autograd Function that binarizes weights.
    Forward: Returns sign(w) -> results in +1 or -1.
    Backward: Returns the incoming gradient as-is (Identity).
    """

    @staticmethod
    def forward(ctx, input_weights):
        # Save the input for the backward pass if needed (not needed for identity STE)
        # We return the sign of the weights. 
        # Note: We use sign() but ensure 0 is treated as +1 to maintain binary state.
        binary_weights = torch.sign(input_weights)
        
        # Replace 0s with 1s (sign(0) is 0 in torch, but we want binary +1/-1)
        binary_weights[binary_weights == 0] = 1
        
        return binary_weights

    @staticmethod
    def backward(ctx, grad_output):
        # Straight Through Estimator: 
        # We pass the gradient back unchanged (identity function).
        # This allows the underlying continuous weights to be updated.
        return grad_output

# Helper function to make it easier to call in layers
def binarize_weights(w):
    return BinaryWeightSTE.apply(w)