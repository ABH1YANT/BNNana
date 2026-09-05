# BNN v6 Evaluation History
Tracking performance of Dense-Residual BNNs with Q1.8 Input Quantization.

## Evaluation Run: 2026-09-05 15:37:06
**Model File:** `best_bnn_v7_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 16 -> 8 |
| **Residual Logic** | Dense Concatenation (Binary Only) |
| **Input Propagation** | Excluded from Residuals (Consumed by L1) |
| **Hardware Sim** | Enabled (Q1.8 Fixed-Point) |
| **Input Features** | 16 |
| **Activation** | BinarySign |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.981134 |
| **Precision** | 0.968668 |
| **Recall** | 0.994434 |
| **F1-Score** | 0.981382 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29035 | 965 |
| **Actual Attack** | 167 | 29834 |

---

## Evaluation Run: 2026-09-05 16:01:32
**Model File:** `best_bnn_v7_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 16 -> 8 |
| **Residual Logic** | Dense Concatenation (Binary Only) |
| **Input Propagation** | Excluded from Residuals (Consumed by L1) |
| **Hardware Sim** | Enabled (Q1.8 Fixed-Point) |
| **Input Features** | 16 |
| **Activation** | BinarySign |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.969817 |
| **Precision** | 0.969833 |
| **Recall** | 0.969801 |
| **F1-Score** | 0.969817 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29095 | 905 |
| **Actual Attack** | 906 | 29095 |

---

## Evaluation Run: 2026-09-05 16:17:53
**Model File:** `best_bnn_v7_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 32 |
| **Residual Logic** | Dense Concatenation (Binary Only) |
| **Input Propagation** | Excluded from Residuals (Consumed by L1) |
| **Hardware Sim** | Enabled (Q1.8 Fixed-Point) |
| **Input Features** | 16 |
| **Activation** | BinarySign |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.977750 |
| **Precision** | 0.976876 |
| **Recall** | 0.978667 |
| **F1-Score** | 0.977771 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29305 | 695 |
| **Actual Attack** | 640 | 29361 |

---

## Evaluation Run: 2026-09-05 18:21:20
**Model File:** `best_bnn_v7_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 64 -> 32 -> 16 |
| **Residual Logic** | Dense Concatenation (Binary Only) |
| **Input Propagation** | Excluded from Residuals (Consumed by L1) |
| **Hardware Sim** | Enabled (Q1.8 Fixed-Point) |
| **Input Features** | 16 |
| **Activation** | BinarySign |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.972350 |
| **Precision** | 0.952748 |
| **Recall** | 0.994000 |
| **F1-Score** | 0.972937 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 28521 | 1479 |
| **Actual Attack** | 180 | 29821 |

---

## Evaluation Run: 2026-09-05 18:29:09
**Model File:** `best_bnn_v7_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 64 -> 32 -> 32 |
| **Residual Logic** | Dense Concatenation (Binary Only) |
| **Input Propagation** | Excluded from Residuals (Consumed by L1) |
| **Hardware Sim** | Enabled (Q1.8 Fixed-Point) |
| **Input Features** | 16 |
| **Activation** | BinarySign |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.980684 |
| **Precision** | 0.983439 |
| **Recall** | 0.977834 |
| **F1-Score** | 0.980629 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29506 | 494 |
| **Actual Attack** | 665 | 29336 |

---

## Evaluation Run: 2026-09-05 18:39:19
**Model File:** `best_bnn_v7_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 64 -> 64 -> 32 |
| **Residual Logic** | Dense Concatenation (Binary Only) |
| **Input Propagation** | Excluded from Residuals (Consumed by L1) |
| **Hardware Sim** | Enabled (Q1.8 Fixed-Point) |
| **Input Features** | 16 |
| **Activation** | BinarySign |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.983100 |
| **Precision** | 0.984684 |
| **Recall** | 0.981467 |
| **F1-Score** | 0.983073 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29542 | 458 |
| **Actual Attack** | 556 | 29445 |

---

## Evaluation Run: 2026-09-05 18:51:49
**Model File:** `best_bnn_v7_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 64 -> 64 -> 64 |
| **Residual Logic** | Dense Concatenation (Binary Only) |
| **Input Propagation** | Excluded from Residuals (Consumed by L1) |
| **Hardware Sim** | Enabled (Q1.8 Fixed-Point) |
| **Input Features** | 16 |
| **Activation** | BinarySign |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.986200 |
| **Precision** | 0.981928 |
| **Recall** | 0.990634 |
| **F1-Score** | 0.986261 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29453 | 547 |
| **Actual Attack** | 281 | 29720 |

---
