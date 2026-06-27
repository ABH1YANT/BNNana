# BNNana

![License](https://img.shields.io/badge/License-MIT-green.svg)

> FPGA-Based Binary Weight Neural Network Accelerator for Real-Time DDoS Detection

BNNana is a hardware/software co-design project that implements a **Binary Weight Neural Network (BWN)** for real-time DDoS detection on an FPGA. The project combines machine learning, digital hardware design, and embedded communication into a complete inference pipeline.

The offline software pipeline trains a BWN using the CICDDoS2019 dataset, exports FPGA-compatible parameters, and generates deployment artifacts. The FPGA receives quantized feature vectors over UART, performs hardware inference, and returns the predicted classification.

---

## Features

* Binary Weight Neural Network implemented in PyTorch
* FPGA inference engine written in Verilog
* Automatic export of weights and thresholds to `.mem` files
* UART-based host ↔ FPGA communication
* Parameterized neural network architecture
* Modular hardware/software co-design

---

## Repository Structure

```text
BNNana/
├── artifacts/         # Exported FPGA artifacts (.mem files, scaler, etc.)
├── datasets/
│   ├── raw/
│   └── processed/
├── fpga/
│   ├── build/         # Vivado project and build outputs
│   ├── constraints/
│   ├── rtl/
│   └── tb/
├── ml/                # Machine learning source code
├── models/            # Trained model checkpoints
├── reports/           # Training and evaluation reports
├── scripts/           # Utility scripts
├── requirements.txt
└── README.md
```

---

## Project Workflow

```text
CICDDoS2019 Dataset
        │
        ▼
 Feature Selection
        │
        ▼
Preprocessing & Quantization
        │
        ▼
 Binary Weight Neural Network
        │
        ▼
weights.mem / thresholds.mem
        │
        ▼
      FPGA
        │
        ▼
UART Classification Result
```

---

## Technology Stack

### Machine Learning

* Python
* PyTorch
* NumPy
* Pandas
* Scikit-learn

### Hardware

* Verilog
* Vivado
* FPGA Block RAM
* UART

---

## Getting Started

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Train the model:

```bash
python ml/train.py
```

Evaluate the trained model:

```bash
python ml/evaluate.py
```

The exported FPGA artifacts will be generated inside the `artifacts/` directory.

---

## Status

This project is under active development.

Current milestones include:

* Machine learning pipeline
* FPGA inference engine
* UART communication
* End-to-end hardware deployment

---

## License

This project is licensed under the MIT License.