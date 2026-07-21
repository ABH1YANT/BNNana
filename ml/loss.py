"""
loss.py
Configurable loss functions for binary classification.
"""

import torch
import torch.nn as nn
from .config import cfg

def get_criterion():
    """
    Factory function for the loss criterion.
    Pull settings from cfg to handle class imbalance.
    """
    # Convert POS_WEIGHT from config to a tensor if it exists
    pos_weight_tensor = None
    if hasattr(cfg, 'POS_WEIGHT') and cfg.POS_WEIGHT is not None:
        pos_weight_tensor = torch.tensor([cfg.POS_WEIGHT], device=cfg.DEVICE)

    # Factory logic for different loss types
    if cfg.LOSS_TYPE == "BCEWithLogits":
        return nn.BCEWithLogitsLoss(pos_weight=pos_weight_tensor)
    
    elif cfg.LOSS_TYPE == "Hinge":
        # Hinge loss is sometimes preferred for BNNs
        return nn.HingeEmbeddingLoss()
        
    else:
        raise ValueError(f"Unsupported LOSS_TYPE: {cfg.LOSS_TYPE}")