"""
loss.py
Configurable loss functions for binary classification.
"""

import torch
import torch.nn as nn

def get_criterion(pos_weight=None):
    """
    Returns Binary Cross Entropy with Logits.
    pos_weight: A tensor scale factor for the positive class (DDoS).
                e.g., torch.tensor([2.0]) if DDoS is underrepresented.
    """
    if pos_weight is not None:
        return nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    return nn.BCEWithLogitsLoss()