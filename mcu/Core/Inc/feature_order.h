
#pragma once

#include <stddef.h>

// Number of input features expected by the BNN.
static constexpr size_t INPUT_FEATURE_COUNT = 16;

// The feature order must match the order used during training.
static const char* const FEATURE_NAMES[INPUT_FEATURE_COUNT] = {
    "Bwd Packet Length Max",
    "Min Packet Length",
    "Subflow Bwd Bytes",
    "Total Length of Bwd Packets",
    "Destination Port",
    "min_seg_size_forward",
    "ACK Flag Count",
    "Subflow Bwd Packets",
    "Fwd Packet Length Max",
    "Total Backward Packets",
    "Subflow Fwd Bytes",
    "Max Packet Length",
    "Total Length of Fwd Packets",
    "Bwd Header Length",
    "Flow Duration",
    "Fwd Header Length"
};
