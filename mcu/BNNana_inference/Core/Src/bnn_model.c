#include "bnn_model.h"
#include "weights.h"
#include "scaler.h"
#include <string.h>

/* Q8.8 Scaling factor (1 / 2^8) */
#define Q8_8_SCALE 0.00390625f

static float hardtanh(float x) {
    if (x > 1.0f) return 1.0f;
    if (x < 0.0f) return 0.0f;
    return x;
}

float bnn_predict(const FlowFeatures *flow) {
    BNN_Input input;
    input.named = *flow;

    // 1. Pre-processing: Normalize inputs
    for (int i = 0; i < BNN_INPUTS; i++) {
        input.array[i] = (input.array[i] - SCALER_MIN[i]) * SCALER_SCALE[i];
        if (input.array[i] < 0.0f) input.array[i] = 0.0f;
        if (input.array[i] > 1.0f) input.array[i] = 1.0f;
    }

    float h0[16], h1[16], h2[16];

    // --- LAYER 0 ---
    for (int j = 0; j < 16; j++) {
        float sum = 0.0f;
        for (int i = 0; i < 17; i++) {
            if (L0_WEIGHTS[j][i] > 0) sum += input.array[i];
            else sum -= input.array[i];
        }
        h0[j] = hardtanh((sum * (float)L0_A[j] * Q8_8_SCALE) + ((float)L0_B[j] * Q8_8_SCALE));
    }

    // --- LAYER 1 ---
    for (int j = 0; j < 16; j++) {
        float sum = 0.0f;
        for (int i = 0; i < 16; i++) {
            if (L1_WEIGHTS[j][i] > 0) sum += h0[i];
            else sum -= h0[i];
        }
        h1[j] = hardtanh((sum * (float)L1_A[j] * Q8_8_SCALE) + ((float)L1_B[j] * Q8_8_SCALE));
    }

    // --- LAYER 2 ---
    for (int j = 0; j < 16; j++) {
        float sum = 0.0f;
        for (int i = 0; i < 16; i++) {
            if (L2_WEIGHTS[j][i] > 0) sum += h1[i];
            else sum -= h1[i];
        }
        h2[j] = hardtanh((sum * (float)L2_A[j] * Q8_8_SCALE) + ((float)L2_B[j] * Q8_8_SCALE));
    }

    // --- OUTPUT LAYER ---
    float final_sum = 0.0f;
    for (int j = 0; j < 16; j++) {
        /* 
         * FIX: Do NOT binarize h2[j]. 
         * PyTorch BinaryLinear uses continuous inputs and binary weights.
         */
        if (OUT_WEIGHTS[0][j] > 0) final_sum += h2[j];
        else final_sum -= h2[j];
    }

    return final_sum + ((float)OUT_BIAS * Q8_8_SCALE);
}

uint8_t bnn_predict_label(const FlowFeatures *flow) {
    return (bnn_predict(flow) > 0.0f) ? 1 : 0;
}