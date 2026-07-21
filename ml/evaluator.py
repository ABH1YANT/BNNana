"""
evaluator.py
Provides the Evaluator class to compute classification metrics.
Essential for comparing different hyperparameter configurations.
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
        Runs inference and calculates standardized classification metrics.
        """
        self.model.eval()
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for inputs, labels in loader:
                inputs = inputs.to(self.device)
                
                # Forward pass (logits)
                logits = self.model(inputs)
                
                # Apply sigmoid to get probabilities for binary classification
                probs = torch.sigmoid(logits)
                preds = (probs > 0.5).float()

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