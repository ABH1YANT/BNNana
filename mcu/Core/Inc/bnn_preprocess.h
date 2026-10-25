
#ifndef BNN_PREPROCESS_H
#define BNN_PREPROCESS_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define BNN_FEATURE_COUNT 16

// Convert 16 raw feature values into the model's Q1.8 inputs.
//
// raw_features: raw, non-negative integer feature values.
// input_q8:      output buffer containing 16 Q1.8 integers.
//
// Returns:
//   0  = success
//  -1  = invalid pointer
//  -2  = invalid feature value
int8_t bnn_preprocess(
    const uint32_t raw_features[BNN_FEATURE_COUNT],
    int16_t input_q8[BNN_FEATURE_COUNT]
);

#ifdef __cplusplus
}
#endif

#endif // BNN_PREPROCESS_H
