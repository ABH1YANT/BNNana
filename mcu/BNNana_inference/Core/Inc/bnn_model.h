#ifndef BNN_MODEL_H
#define BNN_MODEL_H

#include <stdint.h>
#include "bnn_types.h"

/**
 * @brief Performs full 3-layer inference and returns the raw logit.
 */
float bnn_predict(const FlowFeatures *flow);

/**
 * @brief Returns 1 for DDoS, 0 for Benign.
 */
uint8_t bnn_predict_label(const FlowFeatures *flow);

#endif