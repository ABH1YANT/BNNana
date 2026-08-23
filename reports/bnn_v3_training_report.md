# BNN v2 Training & Evaluation History
This report tracks the performance of Binarized Neural Network architectures using Log-Mix scaling.

## Run Date: 2026-08-23 21:09:32
**Evaluated Model:** `best_bnn_v2_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 512 -> 256 -> 128 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Preprocessing** | Log(1+x) + MinMaxScaler |
| **Optimizer** | AdamW |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.9947 |
| **Precision** | 0.9939 |
| **Recall** | 0.9954 |
| **F1-Score** | 0.9947 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29816 | 184 |
| **Actual Attack** | 137 | 29864 |

---
