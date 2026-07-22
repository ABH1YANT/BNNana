"""
ste.py
Implements the Straight Through Estimator (STE) for weight binarization.
This allows gradients to flow through the non-differentiable sign() function.
"""

import torch

class BinaryWeightSTE(torch.autograd.Function):
    """
    Straight Through Estimator for Weights.
    Forward: sign(w) -> {-1, 1}
    Backward: Identity if |w| <= 1, else 0.
    """
    @staticmethod
    def forward(ctx, input_weights):
        ctx.save_for_backward(input_weights)
        binary_weights = torch.sign(input_weights)
        # Force 0 to 1 to maintain strictly binary state
        binary_weights[binary_weights == 0] = 1
        return binary_weights

    @staticmethod
    def backward(ctx, grad_output):
        input_weights, = ctx.saved_tensors
        grad_input = grad_output.clone()
        # Gradient Clipping: Stop updating weights that are already 
        # strongly confident (>1.0 or <-1.0).
        grad_input[input_weights.abs() > 1.0] = 0
        return grad_input

class BinaryActivationSTE(torch.autograd.Function):
    """
    Straight Through Estimator for Activations.
    Forward: sign(x) -> {-1, 1}
    Backward: Identity if |x| <= 1, else 0.
    
    This allows gradients to pass through the discrete sign function 
    during the backward pass.
    """
    @staticmethod
    def forward(ctx, x):
        ctx.save_for_backward(x)
        binary_act = torch.sign(x)
        binary_act[binary_act == 0] = 1
        return binary_act

    @staticmethod
    def backward(ctx, grad_output):
        x, = ctx.saved_tensors
        grad_input = grad_output.clone()
        # Standard BNN "Hardtanh" derivative:
        # We only pass gradients if the input was within the [-1, 1] range.
        grad_input[x.abs() > 1.0] = 0
        return grad_input

def binarize_weights(w):
    """Helper for BinaryLinear layers."""
    return BinaryWeightSTE.apply(w)

def binarize_activation(x):
    """Helper for BinarySign activation layers."""
    return BinaryActivationSTE.apply(x)