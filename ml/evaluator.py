"""
evaluator.py
Standardized inference engine for BNN classification metrics.
Optimized for BNN v6 (Dense Residuals) and Q1.8 hardware simulation.
"""

import torch
import numpy as np
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score, 
    confusion_matrix
)

class Evaluator:
    def __init__(self, model, device):
        """
        Initializes the evaluator.
        :param model: The BNN model (BNNClassifier)
        :param device: torch.device (cpu or cuda)
        """
        self.model = model.to(device)
        self.device = device

    def get_metrics(self, loader):
        """
        Runs inference on the provided DataLoader and calculates hardware-aligned metrics.
        """
        self.model.eval()
        all_preds = []
        all_labels = []

        with torch.no_grad():
            for inputs, labels in loader:
                # Move data to target device
                inputs = inputs.to(self.device)
                
                # Forward pass (returns raw logits from the final BinaryLinear layer)
                logits = self.model(inputs)
                
                # BNN Decision Rule: 
                # In hardware, we don't compute Sigmoid. We check the sign bit.
                # Logit > 0 => Attack (1)
                # Logit <= 0 => Benign (0)
                preds = (logits > 0).int()

                # Collect results
                all_preds.extend(preds.cpu().numpy().flatten())
                all_labels.extend(labels.cpu().numpy().flatten().astype(int))

        # Convert to numpy arrays for metric calculation
        y_true = np.array(all_labels)
        y_pred = np.array(all_preds)

        # Calculate metrics using sklearn
        # zero_division=0 prevents crashes if a class is completely missing in a batch
        results = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
            "confusion_matrix": confusion_matrix(y_true, y_pred).tolist()
        }

        return results

    def predict_single(self, feature_tensor):
        """
        Helper for single-sample inference (useful for real-time testing).
        :param feature_tensor: Tensor of shape (1, INPUT_SIZE)
        """
        self.model.eval()
        with torch.no_grad():
            logit = self.model(feature_tensor.to(self.device))
            return 1 if logit > 0 else 0