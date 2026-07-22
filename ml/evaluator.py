"""
evaluator.py
Standardized inference engine for BNN classification metrics.
"""

import torch
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

class Evaluator:
    def __init__(self, model, device):
        self.model = model.to(device)
        self.device = device

    def get_metrics(self, loader):
        """
        Runs inference and calculates metrics.
        Handles logit-based thresholding for BNNs.
        """
        self.model.eval()
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for inputs, labels in loader:
                inputs = inputs.to(self.device)
                
                # Forward pass (returns raw logits)
                logits = self.model(inputs)
                
                # BNN Decision Rule: 
                # If logit > 0, class is 1 (DDoS). 
                # This is equivalent to sigmoid(x) > 0.5.
                preds = (logits > 0).float()

                all_preds.extend(preds.cpu().numpy().flatten().tolist())
                all_labels.extend(labels.numpy().flatten().tolist())

        # Calculate metrics using sklearn
        results = {
            "accuracy": accuracy_score(all_labels, all_preds),
            "precision": precision_score(all_labels, all_preds, zero_division=0),
            "recall": recall_score(all_labels, all_preds, zero_division=0),
            "f1_score": f1_score(all_labels, all_preds, zero_division=0),
            "confusion_matrix": confusion_matrix(all_labels, all_preds).tolist()
        }

        return results