#include "bnn_model.h"
#include "weights.h"
#include "scaler.h"
#include <string.h>
#include <math.h>

/* Q8.8 Scaling factor (1 / 2^8) */
#define Q8_8_SCALE 0.00390625f

/**
 * @brief Hardtanh activation bounded between 0 and 1.
 * Matches the PyTorch Hardtanh(0, 1) used in the sweep.
 */
static float hardtanh(float x) {
    if (x > 1.0f) return 1.0f;
    if (x < 0.0f) return 0.0f;
    return x;
}

/**
 * @brief BNN Inference Engine (Modular 3-Layer)
 * Fuses Linear Bias + BatchNorm and uses corrected MinMaxScaler math.
 */
float bnn_predict(const FlowFeatures *flow) {
    BNN_Input input;
    input.named = *flow;

    // 1. Pre-processing: Correct MinMaxScaler + Safety Guard
    for (int i = 0; i < BNN_INPUTS; i++) {
        float val = input.array[i];

        // Safety: Handle NaN or Infinity from feature extractor
        if (isnan(val) || isinf(val)) {
            val = 0.0f; 
        }

        // Formula: x_scaled = (x * scale) + offset
        // This matches Scikit-Learn's internal representation exactly
        input.array[i] = (val * SCALER_SCALE[i]) + SCALER_OFFSET[i];

        // Robustness: Clip to [0, 1] range
        if (input.array[i] < 0.0f) input.array[i] = 0.0f;
        if (input.array[i] > 1.0f) input.array[i] = 1.0f;
    }

    // Buffers for hidden layer activations
    float h0[L0_SIZE];
    float h1[L1_SIZE];
    float h2[L2_SIZE];

    // --- LAYER 0: Input -> Hidden 0 ---
    for (int j = 0; j < L0_SIZE; j++) {
        float sum = 0.0f;
        for (int i = 0; i < INPUT_SIZE; i++) {
            if (L0_WEIGHTS[j][i] > 0) sum += input.array[i];
            else sum -= input.array[i];
        }
        // A and B are fused (Linear Bias + BN Mean + BN Beta)
        float val = (sum * (float)L0_A[j] * Q8_8_SCALE) + ((float)L0_B[j] * Q8_8_SCALE);
        h0[j] = hardtanh(val);
    }

    // --- LAYER 1: Hidden 0 -> Hidden 1 ---
    for (int j = 0; j < L1_SIZE; j++) {
        float sum = 0.0f;
        for (int i = 0; i < L0_SIZE; i++) {
            if (L1_WEIGHTS[j][i] > 0) sum += h0[i];
            else sum -= h0[i];
        }
        float val = (sum * (float)L1_A[j] * Q8_8_SCALE) + ((float)L1_B[j] * Q8_8_SCALE);
        h1[j] = hardtanh(val);
    }

    // --- LAYER 2: Hidden 1 -> Hidden 2 ---
    for (int j = 0; j < L2_SIZE; j++) {
        float sum = 0.0f;
        for (int i = 0; i < L1_SIZE; i++) {
            if (L2_WEIGHTS[j][i] > 0) sum += h1[i];
            else sum -= h1[i];
        }
        float val = (sum * (float)L2_A[j] * Q8_8_SCALE) + ((float)L2_B[j] * Q8_8_SCALE);
        h2[j] = hardtanh(val);
    }

    // --- OUTPUT LAYER: Hidden 2 -> Output ---
    float final_sum = 0.0f;
    for (int j = 0; j < L2_SIZE; j++) {
        /* 
         * BinaryLinear in PyTorch uses continuous inputs (h2) 
         * and binary weights (OUT_WEIGHTS). 
         */
        if (OUT_WEIGHTS[0][j] > 0) final_sum += h2[j];
        else final_sum -= h2[j];
    }

    // Add final fused bias
    return final_sum + ((float)OUT_BIAS * Q8_8_SCALE);
}

/**
 * @brief Returns 1 for DDoS, 0 for Benign
 */
uint8_t bnn_predict_label(const FlowFeatures *flow) {
    // Threshold logit at 0.0
    return (bnn_predict(flow) > 0.0f) ? 1 : 0;
}