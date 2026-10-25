
#ifndef BNN_MODEL_H
#define BNN_MODEL_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// Number of input features expected by BNNana.
#define BNN_INPUT_SIZE 16

// Run inference on one preprocessed feature vector.
//
// input_q8: 16 input values in the model's expected Q1.8 format.
// Returns:
//   0 = class 0
//   1 = class 1
int8_t bnn_predict(const int16_t input_q8[BNN_INPUT_SIZE]);

#ifdef __cplusplus
}
#endif

#endif // BNN_MODEL_H
