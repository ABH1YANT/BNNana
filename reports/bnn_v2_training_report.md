# BNN v1 Training & Evaluation History
This report tracks the performance of Binarized Neural Network architectures.

## Run Date: 2026-08-20 12:34:16
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7865 |
| **Precision** | 0.8421 |
| **Recall** | 0.7053 |
| **F1-Score** | 0.7676 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 26033 | 3967 |
| **Actual DDoS** | 8842 | 21159 |

---

## Run Date: 2026-08-20 13:48:28
**Evaluated Model:** `best_bnn_v2_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 8 -> 16 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8523 |
| **Precision** | 0.8126 |
| **Recall** | 0.9158 |
| **F1-Score** | 0.8611 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 23664 | 6336 |
| **Actual DDoS** | 2525 | 27476 |

---

## Run Date: 2026-08-20 13:58:55
**Evaluated Model:** `best_bnn_v2_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 16 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.9118 |
| **Precision** | 0.9370 |
| **Recall** | 0.8830 |
| **F1-Score** | 0.9092 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 28220 | 1780 |
| **Actual DDoS** | 3511 | 26490 |

---

## Run Date: 2026-08-20 15:08:49
**Evaluated Model:** `best_bnn_v2_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 16 -> 8 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.9077 |
| **Precision** | 0.8935 |
| **Recall** | 0.9257 |
| **F1-Score** | 0.9093 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 26688 | 3312 |
| **Actual DDoS** | 2229 | 27772 |

---

## Run Date: 2026-08-20 18:30:10
**Evaluated Model:** `best_bnn_v2_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 16 -> 8 -> 4 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.9042 |
| **Precision** | 0.8919 |
| **Recall** | 0.9199 |
| **F1-Score** | 0.9057 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 26654 | 3346 |
| **Actual DDoS** | 2404 | 27597 |

---

## Run Date: 2026-08-20 19:24:51
**Evaluated Model:** `best_bnn_v2_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8691 |
| **Precision** | 0.9456 |
| **Recall** | 0.7834 |
| **F1-Score** | 0.8569 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 28647 | 1353 |
| **Actual DDoS** | 6499 | 23502 |

---

## Run Date: 2026-08-20 19:44:54
**Evaluated Model:** `best_bnn_v2_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 8 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.9174 |
| **Precision** | 0.8918 |
| **Recall** | 0.9501 |
| **F1-Score** | 0.9200 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 26542 | 3458 |
| **Actual DDoS** | 1498 | 28503 |

---

## Run Date: 2026-08-20 20:53:28
**Evaluated Model:** `best_bnn_v2_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 8 -> 4 -> 2 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8383 |
| **Precision** | 0.7612 |
| **Recall** | 0.9859 |
| **F1-Score** | 0.8591 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 20720 | 9280 |
| **Actual DDoS** | 422 | 29579 |

---

## Run Date: 2026-08-20 21:19:41
**Evaluated Model:** `best_bnn_v2_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 8 -> 8 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8715 |
| **Precision** | 0.8160 |
| **Recall** | 0.9592 |
| **F1-Score** | 0.8819 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 23513 | 6487 |
| **Actual DDoS** | 1223 | 28778 |

---

## Run Date: 2026-08-20 22:13:26
**Evaluated Model:** `best_bnn_v2_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 8 -> 8 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8837 |
| **Precision** | 0.8687 |
| **Recall** | 0.9040 |
| **F1-Score** | 0.8860 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 25902 | 4098 |
| **Actual DDoS** | 2879 | 27122 |

---

## Run Date: 2026-08-20 22:43:24
**Evaluated Model:** `best_bnn_v2_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 8 -> 16 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8590 |
| **Precision** | 0.8092 |
| **Recall** | 0.9394 |
| **F1-Score** | 0.8695 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 23357 | 6643 |
| **Actual DDoS** | 1819 | 28182 |

---
