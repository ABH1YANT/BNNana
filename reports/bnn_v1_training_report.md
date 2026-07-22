# BNN v1 Training & Evaluation History
This report tracks the performance of Binarized Neural Network architectures.

## Run Date: 2026-07-22 17:05:48
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8247 |
| **Precision** | 0.7680 |
| **Recall** | 0.9307 |
| **F1-Score** | 0.8415 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 21563 | 8437 |
| **Actual DDoS** | 2079 | 27922 |

---

## Run Date: 2026-07-22 17:07:19
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.6739 |
| **Precision** | 0.6557 |
| **Recall** | 0.7324 |
| **F1-Score** | 0.6919 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 18462 | 11538 |
| **Actual DDoS** | 8028 | 21973 |

---

## Run Date: 2026-07-22 17:08:46
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8243 |
| **Precision** | 0.7855 |
| **Recall** | 0.8922 |
| **F1-Score** | 0.8355 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 22690 | 7310 |
| **Actual DDoS** | 3233 | 26768 |

---

## Run Date: 2026-07-22 17:10:30
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8912 |
| **Precision** | 0.8333 |
| **Recall** | 0.9780 |
| **F1-Score** | 0.8999 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 24129 | 5871 |
| **Actual DDoS** | 659 | 29342 |

---

## Run Date: 2026-07-22 17:13:10
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8942 |
| **Precision** | 0.8400 |
| **Recall** | 0.9738 |
| **F1-Score** | 0.9020 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 24437 | 5563 |
| **Actual DDoS** | 787 | 29214 |

---

## Run Date: 2026-07-22 17:14:26
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7934 |
| **Precision** | 0.7377 |
| **Recall** | 0.9106 |
| **F1-Score** | 0.8151 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 20287 | 9713 |
| **Actual DDoS** | 2682 | 27319 |

---

## Run Date: 2026-07-22 17:15:26
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8620 |
| **Precision** | 0.8212 |
| **Recall** | 0.9254 |
| **F1-Score** | 0.8702 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 23955 | 6045 |
| **Actual DDoS** | 2237 | 27764 |

---

## Run Date: 2026-07-22 17:17:06
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8139 |
| **Precision** | 0.7477 |
| **Recall** | 0.9477 |
| **F1-Score** | 0.8359 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 20404 | 9596 |
| **Actual DDoS** | 1568 | 28433 |

---

## Run Date: 2026-07-22 17:19:20
**Evaluated Model:** `best_bwn_model.pth`

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
| **Accuracy** | 0.7058 |
| **Precision** | 0.6571 |
| **Recall** | 0.8611 |
| **F1-Score** | 0.7454 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 16517 | 13483 |
| **Actual DDoS** | 4167 | 25834 |

---

## Run Date: 2026-07-22 17:20:56
**Evaluated Model:** `best_bwn_model.pth`

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
| **Accuracy** | 0.8241 |
| **Precision** | 0.7471 |
| **Recall** | 0.9799 |
| **F1-Score** | 0.8478 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 20050 | 9950 |
| **Actual DDoS** | 602 | 29399 |

---

## Run Date: 2026-07-22 17:22:06
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 16 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.6610 |
| **Precision** | 0.6369 |
| **Recall** | 0.7490 |
| **F1-Score** | 0.6884 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 17190 | 12810 |
| **Actual DDoS** | 7531 | 22470 |

---

## Run Date: 2026-07-22 17:23:49
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 16 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7579 |
| **Precision** | 0.6971 |
| **Recall** | 0.9120 |
| **F1-Score** | 0.7902 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 18112 | 11888 |
| **Actual DDoS** | 2641 | 27360 |

---

## Run Date: 2026-07-22 17:25:44
**Evaluated Model:** `best_bwn_model.pth`

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
| **Accuracy** | 0.8613 |
| **Precision** | 0.8388 |
| **Recall** | 0.8945 |
| **F1-Score** | 0.8658 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 24843 | 5157 |
| **Actual DDoS** | 3164 | 26837 |

---

## Run Date: 2026-07-22 17:27:48
**Evaluated Model:** `best_bwn_model.pth`

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
| **Accuracy** | 0.9104 |
| **Precision** | 0.8601 |
| **Recall** | 0.9802 |
| **F1-Score** | 0.9162 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 25216 | 4784 |
| **Actual DDoS** | 593 | 29408 |

---

## Run Date: 2026-07-22 17:28:53
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 8 -> 16 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8307 |
| **Precision** | 0.7984 |
| **Recall** | 0.8849 |
| **F1-Score** | 0.8394 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 23295 | 6705 |
| **Actual DDoS** | 3453 | 26548 |

---

## Run Date: 2026-07-22 17:30:21
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 8 -> 16 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8389 |
| **Precision** | 0.7661 |
| **Recall** | 0.9758 |
| **F1-Score** | 0.8583 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 21061 | 8939 |
| **Actual DDoS** | 726 | 29275 |

---

## Run Date: 2026-07-22 17:32:06
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 24 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8122 |
| **Precision** | 0.8066 |
| **Recall** | 0.8214 |
| **F1-Score** | 0.8139 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 24091 | 5909 |
| **Actual DDoS** | 5358 | 24643 |

---

## Run Date: 2026-07-22 17:33:29
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 24 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8193 |
| **Precision** | 0.7589 |
| **Recall** | 0.9360 |
| **F1-Score** | 0.8382 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 21079 | 8921 |
| **Actual DDoS** | 1920 | 28081 |

---

## Run Date: 2026-07-22 17:35:21
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 24 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8621 |
| **Precision** | 0.7996 |
| **Recall** | 0.9664 |
| **F1-Score** | 0.8751 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 22732 | 7268 |
| **Actual DDoS** | 1008 | 28993 |

---

## Run Date: 2026-07-22 17:36:48
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 24 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8019 |
| **Precision** | 0.7469 |
| **Recall** | 0.9131 |
| **F1-Score** | 0.8217 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 20718 | 9282 |
| **Actual DDoS** | 2606 | 27395 |

---

## Run Date: 2026-07-22 17:38:36
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
| **Accuracy** | 0.8584 |
| **Precision** | 0.8450 |
| **Recall** | 0.8778 |
| **F1-Score** | 0.8611 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 25168 | 4832 |
| **Actual DDoS** | 3666 | 26335 |

---

## Run Date: 2026-07-22 17:40:38
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
| **Accuracy** | 0.8335 |
| **Precision** | 0.7733 |
| **Recall** | 0.9438 |
| **F1-Score** | 0.8501 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 21697 | 8303 |
| **Actual DDoS** | 1686 | 28315 |

---

## Run Date: 2026-07-22 17:42:26
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8012 |
| **Precision** | 0.7219 |
| **Recall** | 0.9798 |
| **F1-Score** | 0.8313 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 18678 | 11322 |
| **Actual DDoS** | 606 | 29395 |

---

## Run Date: 2026-07-22 17:43:46
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7330 |
| **Precision** | 0.7449 |
| **Recall** | 0.7086 |
| **F1-Score** | 0.7263 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 22721 | 7279 |
| **Actual DDoS** | 8743 | 21258 |

---

## Run Date: 2026-07-22 17:46:33
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 32 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8569 |
| **Precision** | 0.8539 |
| **Recall** | 0.8612 |
| **F1-Score** | 0.8575 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 25578 | 4422 |
| **Actual DDoS** | 4164 | 25837 |

---

## Run Date: 2026-07-22 17:49:29
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 32 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8919 |
| **Precision** | 0.8373 |
| **Recall** | 0.9728 |
| **F1-Score** | 0.8999 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 24328 | 5672 |
| **Actual DDoS** | 817 | 29184 |

---

## Run Date: 2026-07-22 17:51:03
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 32 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7699 |
| **Precision** | 0.6987 |
| **Recall** | 0.9490 |
| **F1-Score** | 0.8049 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 17722 | 12278 |
| **Actual DDoS** | 1529 | 28472 |

---

## Run Date: 2026-07-22 17:52:18
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 32 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8472 |
| **Precision** | 0.7846 |
| **Recall** | 0.9571 |
| **F1-Score** | 0.8623 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 22117 | 7883 |
| **Actual DDoS** | 1288 | 28713 |

---

## Run Date: 2026-07-22 17:54:43
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 24 -> 16 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8187 |
| **Precision** | 0.7691 |
| **Recall** | 0.9110 |
| **F1-Score** | 0.8340 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 21795 | 8205 |
| **Actual DDoS** | 2671 | 27330 |

---

## Run Date: 2026-07-22 17:56:50
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 24 -> 16 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7934 |
| **Precision** | 0.7232 |
| **Recall** | 0.9508 |
| **F1-Score** | 0.8215 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 19080 | 10920 |
| **Actual DDoS** | 1477 | 28524 |

---

## Run Date: 2026-07-22 17:57:44
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 24 -> 16 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.5078 |
| **Precision** | 0.5047 |
| **Recall** | 0.8515 |
| **F1-Score** | 0.6337 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 4925 | 25075 |
| **Actual DDoS** | 4455 | 25546 |

---

## Run Date: 2026-07-22 17:59:34
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 24 -> 16 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7941 |
| **Precision** | 0.7323 |
| **Recall** | 0.9271 |
| **F1-Score** | 0.8182 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 19831 | 10169 |
| **Actual DDoS** | 2188 | 27813 |

---

## Run Date: 2026-07-22 18:01:34
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 8 -> 16 -> 24 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8736 |
| **Precision** | 0.8249 |
| **Recall** | 0.9484 |
| **F1-Score** | 0.8824 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 23960 | 6040 |
| **Actual DDoS** | 1547 | 28454 |

---

## Run Date: 2026-07-22 18:03:10
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 8 -> 16 -> 24 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8539 |
| **Precision** | 0.7854 |
| **Recall** | 0.9740 |
| **F1-Score** | 0.8696 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 22017 | 7983 |
| **Actual DDoS** | 781 | 29220 |

---

## Run Date: 2026-07-22 18:04:25
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 8 -> 16 -> 24 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8435 |
| **Precision** | 0.8050 |
| **Recall** | 0.9066 |
| **F1-Score** | 0.8527 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 23410 | 6590 |
| **Actual DDoS** | 2803 | 27198 |

---

## Run Date: 2026-07-22 18:06:00
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 8 -> 16 -> 24 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8301 |
| **Precision** | 0.7603 |
| **Recall** | 0.9641 |
| **F1-Score** | 0.8501 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 20879 | 9121 |
| **Actual DDoS** | 1076 | 28925 |

---

## Run Date: 2026-07-22 18:08:29
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 -> 16 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7903 |
| **Precision** | 0.7483 |
| **Recall** | 0.8749 |
| **F1-Score** | 0.8067 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 21170 | 8830 |
| **Actual DDoS** | 3752 | 26249 |

---

## Run Date: 2026-07-22 18:10:22
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 -> 16 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7517 |
| **Precision** | 0.7232 |
| **Recall** | 0.8157 |
| **F1-Score** | 0.7667 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 20633 | 9367 |
| **Actual DDoS** | 5529 | 24472 |

---

## Run Date: 2026-07-22 18:11:37
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 -> 16 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7106 |
| **Precision** | 0.7689 |
| **Recall** | 0.6021 |
| **F1-Score** | 0.6754 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 24572 | 5428 |
| **Actual DDoS** | 11937 | 18064 |

---

## Run Date: 2026-07-22 18:13:06
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 16 -> 16 -> 16 -> 16 -> 16 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.8108 |
| **Precision** | 0.7766 |
| **Recall** | 0.8727 |
| **F1-Score** | 0.8218 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 22467 | 7533 |
| **Actual DDoS** | 3820 | 26181 |

---

## Run Date: 2026-07-22 18:14:33
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 32 -> 32 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.6709 |
| **Precision** | 0.6702 |
| **Recall** | 0.6729 |
| **F1-Score** | 0.6716 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 20067 | 9933 |
| **Actual DDoS** | 9813 | 20188 |

---

## Run Date: 2026-07-22 18:16:32
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 32 -> 32 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7884 |
| **Precision** | 0.7318 |
| **Recall** | 0.9104 |
| **F1-Score** | 0.8114 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 19989 | 10011 |
| **Actual DDoS** | 2688 | 27313 |

---

## Run Date: 2026-07-22 18:18:33
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 32 -> 32 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7925 |
| **Precision** | 0.7165 |
| **Recall** | 0.9680 |
| **F1-Score** | 0.8235 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 18508 | 11492 |
| **Actual DDoS** | 959 | 29042 |

---

## Run Date: 2026-07-22 18:20:00
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 32 -> 32 -> 32 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7599 |
| **Precision** | 0.7005 |
| **Recall** | 0.9080 |
| **F1-Score** | 0.7909 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 18355 | 11645 |
| **Actual DDoS** | 2761 | 27240 |

---

## Run Date: 2026-07-22 18:21:02
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 24 -> 16 -> 8 -> 4 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7069 |
| **Precision** | 0.6836 |
| **Recall** | 0.7704 |
| **F1-Score** | 0.7244 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 19301 | 10699 |
| **Actual DDoS** | 6889 | 23112 |

---

## Run Date: 2026-07-22 18:22:16
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 24 -> 16 -> 8 -> 4 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.5505 |
| **Precision** | 0.5337 |
| **Recall** | 0.7991 |
| **F1-Score** | 0.6400 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 9057 | 20943 |
| **Actual DDoS** | 6027 | 23974 |

---

## Run Date: 2026-07-22 18:23:25
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 24 -> 16 -> 8 -> 4 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.4994 |
| **Precision** | 0.4997 |
| **Recall** | 0.9986 |
| **F1-Score** | 0.6661 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 7 | 29993 |
| **Actual DDoS** | 43 | 29958 |

---

## Run Date: 2026-07-22 18:24:52
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 24 -> 16 -> 8 -> 4 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.5716 |
| **Precision** | 0.5436 |
| **Recall** | 0.8922 |
| **F1-Score** | 0.6756 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 7532 | 22468 |
| **Actual DDoS** | 3235 | 26766 |

---

## Run Date: 2026-07-22 18:25:54
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 16 -> 16 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.7080 |
| **Precision** | 0.6701 |
| **Recall** | 0.8197 |
| **F1-Score** | 0.7374 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 17891 | 12109 |
| **Actual DDoS** | 5409 | 24592 |

---

## Run Date: 2026-07-22 18:28:08
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 16 -> 16 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | Adam |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.6994 |
| **Precision** | 0.6629 |
| **Recall** | 0.8116 |
| **F1-Score** | 0.7297 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 17616 | 12384 |
| **Actual DDoS** | 5653 | 24348 |

---

## Run Date: 2026-07-22 18:29:29
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 16 -> 16 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.6728 |
| **Precision** | 0.6529 |
| **Recall** | 0.7380 |
| **F1-Score** | 0.6929 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 18229 | 11771 |
| **Actual DDoS** | 7859 | 22142 |

---

## Run Date: 2026-07-22 18:30:37
**Evaluated Model:** `best_bwn_model.pth`

### 1. Model Configuration
| Parameter | Value |
| :--- | :--- |
| **Architecture** | 32 -> 32 -> 16 -> 16 -> 8 |
| **Activation** | BinarySign |
| **Hardware Simulation** | Enabled (Q8.8) |
| **Optimizer** | SGD |
| **Loss Function** | BCEWithLogits |

### 2. Performance Metrics
| Metric | Score |
| :--- | :--- |
| **Accuracy** | 0.6003 |
| **Precision** | 0.5829 |
| **Recall** | 0.7052 |
| **F1-Score** | 0.6383 |

### 3. Confusion Matrix
| | Predicted Benign | Predicted DDoS |
| :--- | :---: | :---: |
| **Actual Benign** | 14864 | 15136 |
| **Actual DDoS** | 8845 | 21156 |

---
