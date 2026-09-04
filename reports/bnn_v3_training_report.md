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

## Evaluation Run: 2026-09-04 09:24:31

**Model File:** `best_bnn_v3_model.pth`

### 1. System Configuration

| Parameter | Value |
| :--- | :--- |
| **Architecture** | 128 -> 64 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8 Fixed-Point) |
| **Preprocessing** | LUT + Representative + log1p + MinMax |
| **Dataset** | scaled_dataset.csv |
| **Features Used** | 16 Behavioral Features |

### 2. Performance Metrics

| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.994200 |
| **Precision** | 0.995953 |
| **Recall** | 0.992434 |
| **F1-Score** | 0.994190 |

### 3. Confusion Matrix

| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29879 | 121 |
| **Actual Attack** | 227 | 29774 |

---


## Evaluation Run: 2026-09-04 09:30:47

**Model File:** `best_bnn_v3_model.pth`

### 1. System Configuration

| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8 Fixed-Point) |
| **Preprocessing** | LUT + Representative + log1p + MinMax |
| **Dataset** | scaled_dataset.csv |
| **Features Used** | 16 Behavioral Features |

### 2. Performance Metrics

| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.889452 |
| **Precision** | 0.837045 |
| **Recall** | 0.967201 |
| **F1-Score** | 0.897428 |

### 3. Confusion Matrix

| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 24351 | 5649 |
| **Actual Attack** | 984 | 29017 |

---


## Evaluation Run: 2026-09-04 09:55:17

**Model File:** `best_bnn_v4_model.pth`

### 1. System Configuration

| Parameter | Value |
| :--- | :--- |
| **Architecture** | 64 -> 32 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8 Fixed-Point) |
| **Preprocessing** | LUT + Representative + log1p + MinMax |
| **Dataset** | scaled_dataset.csv |
| **Features Used** | 16 Behavioral Features |

### 2. Performance Metrics

| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.992750 |
| **Precision** | 0.990771 |
| **Recall** | 0.994767 |
| **F1-Score** | 0.992765 |

### 3. Confusion Matrix

| | Predicted Benign | Predicted Attack |
| :--- | :---: | :---: |
| **Actual Benign** | 29722 | 278 |
| **Actual Attack** | 157 | 29844 |

---

