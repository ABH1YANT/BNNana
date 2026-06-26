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
        Runs inference on the provided loader and calculates metrics.
        Returns a dictionary of results.
        """
        self.model.eval()
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for inputs, labels in loader:
                inputs = inputs.to(self.device)
                
                # Forward pass (outputs are logits)
                logits = self.model(inputs).squeeze()
                
                # Convert logits to probabilities then to binary (0 or 1)
                # On FPGA, this is equivalent to checking if the final sum > threshold
                probs = torch.sigmoid(logits)
                preds = (probs > 0.5).cpu().numpy()
                
                all_preds.extend(preds)
                all_labels.extend(labels.numpy())

        # Calculate standard ML metrics
        metrics = {
            "accuracy": accuracy_score(all_labels, all_preds),
            "precision": precision_score(all_labels, all_preds),
            "recall": recall_score(all_labels, all_preds),
            "f1_score": f1_score(all_labels, all_preds),
            "confusion_matrix": confusion_matrix(all_labels, all_preds).tolist()
        }
        
        return metrics