#ifndef BNN_WEIGHTS_H
#define BNN_WEIGHTS_H
#include <stdint.h>
#define NUM_HIDDEN_LAYERS 3
#define INPUT_SIZE 17
extern const int8_t L0_WEIGHTS[16][17];
extern const int16_t L0_A[16];
extern const int16_t L0_B[16];
extern const int8_t L1_WEIGHTS[16][16];
extern const int16_t L1_A[16];
extern const int16_t L1_B[16];
extern const int8_t L2_WEIGHTS[16][16];
extern const int16_t L2_A[16];
extern const int16_t L2_B[16];
extern const int8_t OUT_WEIGHTS[1][16];
extern const int16_t OUT_BIAS;
#endif