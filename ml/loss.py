"""
loss.py
Configurable loss functions for binary classification.
"""

import torch
import torch.nn as nn
from .config import cfg

class SquaredHingeLoss(nn.Module):
    """
    Commonly used in BNN research. 
    It encourages the model to produce logits with a magnitude >= 1.
    Expects targets to be 0 or 1 (internally converts to -1 or 1).
    """
    def __init__(self):
        super(SquaredHingeLoss, self).__init__()

    def forward(self, outputs, targets):
        # Convert 0/1 targets to -1/1 for Hinge math
        targets_m1_p1 = 2 * targets - 1
        # L = mean(max(0, 1 - y_true * y_pred)^2)
        loss = torch.mean(torch.clamp(1 - outputs * targets_m1_p1, min=0)**2)
        return loss

def get_criterion():
    """
    Factory function for the loss criterion.
    All settings are controlled via config.py.
    """
    
    # 1. Handle Positive Class Weighting (Critical for DDoS imbalance)
    pos_weight_tensor = None
    if hasattr(cfg, 'POS_WEIGHT') and cfg.POS_WEIGHT is not None:
        pos_weight_tensor = torch.tensor([cfg.POS_WEIGHT], device=cfg.DEVICE)

    # 2. Select Loss Type based on config
    if cfg.LOSS_TYPE == "BCEWithLogits":
        # Best for general stability and handling class imbalance via pos_weight
        return nn.BCEWithLogitsLoss(pos_weight=pos_weight_tensor)
    
    elif cfg.LOSS_TYPE == "SquaredHinge":
        # Often yields better results for BNNs by pushing logits away from zero
        return SquaredHingeLoss()
    
    elif cfg.LOSS_TYPE == "Hinge":
        # Standard Hinge Loss
        return nn.HingeEmbeddingLoss()
        
    else:
        raise ValueError(f"Unsupported LOSS_TYPE: {cfg.LOSS_TYPE}. "
                         "Check your config.py settings.")