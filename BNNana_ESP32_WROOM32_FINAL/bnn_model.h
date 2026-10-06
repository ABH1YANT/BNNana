#pragma once
#include <Arduino.h>
#include <stdint.h>

#define BNN_INPUTS 16
#define BNN_L0_OUT 64
#define BNN_L1_OUT 64
#define BNN_L2_OUT 32
#define BNN_OUTPUT_INPUTS 160

// Input expected by the exported FPGA model:
// unsigned Q1.8 byte, 0..255, representing x/256.0.
extern const uint16_t L0_WEIGHTS[BNN_L0_OUT];
extern const int16_t  L0_THRESHOLDS[BNN_L0_OUT];

extern const uint32_t L1_WEIGHTS[BNN_L1_OUT][2];
extern const uint16_t L1_THRESHOLDS[BNN_L1_OUT];

extern const uint32_t L2_WEIGHTS[BNN_L2_OUT][4];
extern const uint16_t L2_THRESHOLDS[BNN_L2_OUT];

extern const uint32_t OUT_WEIGHTS[5];
extern const uint16_t OUT_THRESHOLD;

// Runs the exact exported threshold network.
// x_q8: 16 values in [0,255].
// Returns 0 or 1.
uint8_t bnn_predict_q8(const uint8_t x_q8[BNN_INPUTS]);

// Debug variant: returns layer activations if desired.
void bnn_forward_q8(const uint8_t x_q8[BNN_INPUTS],
                    uint8_t l0[BNN_L0_OUT],
                    uint8_t l1[BNN_L1_OUT],
                    uint8_t l2[BNN_L2_OUT],
                    uint8_t *out);
