#include "bnn_model.h"
#include "weights.h"
#include "scaler.h"
#include <string.h>

/* Q8.8 Scaling factor (1 / 2^8) */
#define Q8_8_SCALE 0.00390625f

/**
 * @brief Hardtanh activation bounded between 0 and 1.
 */
static float hardtanh(float x) {
    if (x > 1.0f) return 1.0f;
    if (x < 0.0f) return 0.0f;
    return x;
}

/**
 * @brief BNN Inference Engine (Modular 3-Layer)
 * Architecture: 17 -> 16 -> 16 -> 16 -> 1
 */
float bnn_predict(const FlowFeatures *flow) {
    BNN_Input input;
    input.named = *flow;

    // 1. Pre-processing: Normalize inputs using MinMaxScaler
    // This uses the SCALER_MIN and SCALER_SCALE from scaler.c
    for (int i = 0; i < BNN_INPUTS; i++) {
        input.array[i] = (input.array[i] - SCALER_MIN[i]) * SCALER_SCALE[i];
        if (input.array[i] < 0.0f) input.array[i] = 0.0f;
        if (input.array[i] > 1.0f) input.array[i] = 1.0f;
    }

    // Buffers for hidden layer activations (16 neurons each)
    float h0[16];
    float h1[16];
    float h2[16];

    // --- LAYER 0: Input (17) -> Hidden 0 (16) ---
    for (int j = 0; j < 16; j++) {
        float sum = 0.0f;
        for (int i = 0; i < 17; i++) {
            if (L0_WEIGHTS[j][i] > 0) sum += input.array[i];
            else sum -= input.array[i];
        }
        float val = (sum * (float)L0_A[j] * Q8_8_SCALE) + ((float)L0_B[j] * Q8_8_SCALE);
        h0[j] = hardtanh(val);
    }

    // --- LAYER 1: Hidden 0 (16) -> Hidden 1 (16) ---
    for (int j = 0; j < 16; j++) {
        float sum = 0.0f;
        for (int i = 0; i < 16; i++) {
            // BWN logic: Weights are binary, activations are floats
            if (L1_WEIGHTS[j][i] > 0) sum += h0[i];
            else sum -= h0[i];
        }
        float val = (sum * (float)L1_A[j] * Q8_8_SCALE) + ((float)L1_B[j] * Q8_8_SCALE);
        h1[j] = hardtanh(val);
    }

    // --- LAYER 2: Hidden 1 (16) -> Hidden 2 (16) ---
    for (int j = 0; j < 16; j++) {
        float sum = 0.0f;
        for (int i = 0; i < 16; i++) {
            if (L2_WEIGHTS[j][i] > 0) sum += h1[i];
            else sum -= h1[i];
        }
        float val = (sum * (float)L2_A[j] * Q8_8_SCALE) + ((float)L2_B[j] * Q8_8_SCALE);
        h2[j] = hardtanh(val);
    }

    // --- OUTPUT LAYER: Hidden 2 (16) -> Output (1) ---
    float final_sum = 0.0f;
    for (int j = 0; j < 16; j++) {
        /*
         * Binarize the final hidden layer activations to +1/-1 
         * to match the binary weights of the output layer.
         * Threshold is 0.5 because Hardtanh is 0 to 1.
         */
        float bit = (h2[j] > 0.5f) ? 1.0f : -1.0f;
        
        if (OUT_WEIGHTS[0][j] > 0) final_sum += bit;
        else final_sum -= bit;
    }

    // Add final bias (Converted from Q8.8)
    float final_bias = (float)OUT_BIAS * Q8_8_SCALE;

    return final_sum + final_bias;
}

/**
 * @brief Returns 1 for DDoS, 0 for Benign
 */
uint8_t bnn_predict_label(const FlowFeatures *flow) {
    // Threshold the final logit at 0.0
    return (bnn_predict(flow) > 0.0f) ? 1 : 0;
}