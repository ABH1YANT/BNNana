# BNN v2 Training & Evaluation History
This report tracks Binarized Neural Network performance using LUT-based preprocessing.

## Evaluation Run: 2026-09-04 10:20:55

**Model File:** `best_bnn_v5_model.pth`

### 1. System Configuration

| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8 Fixed-Point) |
| **Preprocessing** | LUT + Representative + log1p + MinMax |
| **Dataset** | scaled_dataset.csv |
| **Features Used** | 16 Behavioral Features |

### 2. Performance Metrics

| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.987184 |
| **Precision** | 0.976557 |
| **Recall** | 0.998333 |
| **F1-Score** | 0.987325 |

### 3. Confusion Matrix

| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29281 | 719 |
| **Actual Attack** | 50 | 29951 |

---


## Evaluation Run: 2026-09-04 10:38:06

**Model File:** `best_bnn_v6_model.pth`

### 1. System Configuration

| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 16 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8 Fixed-Point) |
| **Preprocessing** | LUT + Representative + log1p + MinMax |
| **Dataset** | scaled_dataset.csv |
| **Features Used** | 16 Behavioral Features |

### 2. Performance Metrics

| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.980900 |
| **Precision** | 0.966472 |
| **Recall** | 0.996367 |
| **F1-Score** | 0.981192 |

### 3. Confusion Matrix

| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 28963 | 1037 |
| **Actual Attack** | 109 | 29892 |

---

