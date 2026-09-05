# BNN v6 Evaluation History
Tracking performance of Dense-Residual Binarized Neural Networks.

## Evaluation Run: 2026-09-04 20:26:31
**Model File:** `best_bnn_v6_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 8 -> 16 -> 32 |
| **Residuals** | Dense (Concatenation) |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q1.8 Fixed-Point) |
| **Preprocessing** | LUT + log1p + MinMax |
| **Input Features** | 16 |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.957334 |
| **Precision** | 0.948720 |
| **Recall** | 0.966934 |
| **F1-Score** | 0.957740 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 28432 | 1568 |
| **Actual Attack** | 992 | 29009 |

---

## Evaluation Run: 2026-09-04 20:42:59
**Model File:** `best_bnn_v6_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 16 -> 8 |
| **Residuals** | Dense (Concatenation) |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q1.8 Fixed-Point) |
| **Preprocessing** | LUT + log1p + MinMax |
| **Input Features** | 16 |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.980450 |
| **Precision** | 0.976118 |
| **Recall** | 0.985000 |
| **F1-Score** | 0.980539 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29277 | 723 |
| **Actual Attack** | 450 | 29551 |

---

## Evaluation Run: 2026-09-04 21:14:35
**Model File:** `best_bnn_v6_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 16 -> 16 |
| **Residuals** | Dense (Concatenation) |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q1.8 Fixed-Point) |
| **Preprocessing** | LUT + log1p + MinMax |
| **Input Features** | 16 |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.986684 |
| **Precision** | 0.977938 |
| **Recall** | 0.995833 |
| **F1-Score** | 0.986805 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29326 | 674 |
| **Actual Attack** | 125 | 29876 |

---

## Evaluation Run: 2026-09-04 23:00:42
**Model File:** `best_bnn_v6_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 64 -> 32 -> 32 -> 16 |
| **Residuals** | None |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q1.8 Fixed-Point) |
| **Preprocessing** | LUT + log1p + MinMax |
| **Input Features** | 16 |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.995300 |
| **Precision** | 0.995333 |
| **Recall** | 0.995267 |
| **F1-Score** | 0.995300 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29860 | 140 |
| **Actual Attack** | 142 | 29859 |

---

## Evaluation Run: 2026-09-04 23:15:40
**Model File:** `best_bnn_v6_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 64 -> 32 -> 16 |
| **Residuals** | None |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q1.8 Fixed-Point) |
| **Preprocessing** | LUT + log1p + MinMax |
| **Input Features** | 16 |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.997333 |
| **Precision** | 0.995879 |
| **Recall** | 0.998800 |
| **F1-Score** | 0.997337 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29876 | 124 |
| **Actual Attack** | 36 | 29965 |

---

## Evaluation Run: 2026-09-04 23:24:12
**Model File:** `best_bnn_v6_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 16 -> 16 |
| **Residuals** | None |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q1.8 Fixed-Point) |
| **Preprocessing** | LUT + log1p + MinMax |
| **Input Features** | 16 |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.988384 |
| **Precision** | 0.983532 |
| **Recall** | 0.993400 |
| **F1-Score** | 0.988442 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29501 | 499 |
| **Actual Attack** | 198 | 29803 |

---

## Evaluation Run: 2026-09-04 23:36:46
**Model File:** `best_bnn_v6_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 24 -> 16 |
| **Residuals** | None |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q1.8 Fixed-Point) |
| **Preprocessing** | LUT + log1p + MinMax |
| **Input Features** | 16 |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.990550 |
| **Precision** | 0.985613 |
| **Recall** | 0.995633 |
| **F1-Score** | 0.990598 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29564 | 436 |
| **Actual Attack** | 131 | 29870 |

---

## Evaluation Run: 2026-09-04 23:53:20
**Model File:** `best_bnn_v6_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 8 |
| **Residual Logic** | Standard Sequential |
| **Input Propagation** | N/A |
| **Hardware Sim** | Enabled (Q1.8 Fixed-Point) |
| **Input Features** | 16 |
| **Activation** | BinarySign |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.968351 |
| **Precision** | 0.981001 |
| **Recall** | 0.955201 |
| **F1-Score** | 0.967929 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29445 | 555 |
| **Actual Attack** | 1344 | 28657 |

---

## Evaluation Run: 2026-09-05 00:22:28
**Model File:** `best_bnn_v6_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 12 -> 8 |
| **Residual Logic** | Dense Concatenation (Binary Only) |
| **Input Propagation** | Excluded from Residuals (Consumed by L1) |
| **Hardware Sim** | Enabled (Q1.8 Fixed-Point) |
| **Input Features** | 16 |
| **Activation** | BinarySign |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.952601 |
| **Precision** | 0.917890 |
| **Recall** | 0.994134 |
| **F1-Score** | 0.954492 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 27332 | 2668 |
| **Actual Attack** | 176 | 29825 |

---

## Evaluation Run: 2026-09-05 00:34:52
**Model File:** `best_bnn_v6_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 |
| **Residual Logic** | Dense Concatenation (Binary Only) |
| **Input Propagation** | Excluded from Residuals (Consumed by L1) |
| **Hardware Sim** | Enabled (Q1.8 Fixed-Point) |
| **Input Features** | 16 |
| **Activation** | BinarySign |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.987100 |
| **Precision** | 0.977768 |
| **Recall** | 0.996867 |
| **F1-Score** | 0.987225 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29320 | 680 |
| **Actual Attack** | 94 | 29907 |

---

## Evaluation Run: 2026-09-05 00:40:34
**Model File:** `best_bnn_v6_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 |
| **Residual Logic** | Dense Concatenation (Binary Only) |
| **Input Propagation** | Excluded from Residuals (Consumed by L1) |
| **Hardware Sim** | Enabled (Q1.8 Fixed-Point) |
| **Input Features** | 16 |
| **Activation** | BinarySign |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.975250 |
| **Precision** | 0.973153 |
| **Recall** | 0.977467 |
| **F1-Score** | 0.975306 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29191 | 809 |
| **Actual Attack** | 676 | 29325 |

---

## Evaluation Run: 2026-09-05 00:45:09
**Model File:** `best_bnn_v6_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 |
| **Residual Logic** | Dense Concatenation (Binary Only) |
| **Input Propagation** | Excluded from Residuals (Consumed by L1) |
| **Hardware Sim** | Enabled (Q1.8 Fixed-Point) |
| **Input Features** | 16 |
| **Activation** | BinarySign |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.972167 |
| **Precision** | 0.968080 |
| **Recall** | 0.976534 |
| **F1-Score** | 0.972289 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29034 | 966 |
| **Actual Attack** | 704 | 29297 |

---

## Evaluation Run: 2026-09-05 00:59:29
**Model File:** `best_bnn_v6_model.pth`

### 1. System Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 20 -> 20 -> 20 |
| **Residual Logic** | Dense Concatenation (Binary Only) |
| **Input Propagation** | Excluded from Residuals (Consumed by L1) |
| **Hardware Sim** | Enabled (Q1.8 Fixed-Point) |
| **Input Features** | 16 |
| **Activation** | BinarySign |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.982517 |
| **Precision** | 0.983468 |
| **Recall** | 0.981534 |
| **F1-Score** | 0.982500 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29505 | 495 |
| **Actual Attack** | 554 | 29447 |

---
