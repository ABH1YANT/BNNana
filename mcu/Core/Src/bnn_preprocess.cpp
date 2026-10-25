
#include "bnn_preprocess.h"
#include "bnn_luts.h"

#include <stddef.h>
#include <stdint.h>

// Look up one feature's unsigned normalized Q8 value.
// Returns false if the calculated bucket is outside the table.
static bool lookup_feature(
    uint32_t raw_value,
    uint8_t shift,
    const uint8_t* lut,
    uint32_t lut_size,
    uint8_t* result)
{
    if (lut == nullptr || result == nullptr || lut_size == 0) {
        return false;
    }

    const uint32_t bucket = raw_value >> shift;

    if (bucket >= lut_size) {
        return false;
    }

    *result = lut[bucket];
    return true;
}

extern "C" int8_t bnn_preprocess(
    const uint32_t raw_features[BNN_FEATURE_COUNT],
    int16_t input_q8[BNN_FEATURE_COUNT])
{
    if (raw_features == nullptr || input_q8 == nullptr) {
        return -1;
    }

    uint8_t value = 0;

    // Feature 0: Bwd Packet Length Max
    if (!lookup_feature(
            raw_features[0],
            BNN_LUT_0_SHIFT,
            BNN_LUT_0,
            BNN_LUT_0_SIZE,
            &value)) {
        return -2;
    }
    input_q8[0] = value;

    // Feature 1: Min Packet Length
    if (!lookup_feature(
            raw_features[1],
            BNN_LUT_1_SHIFT,
            BNN_LUT_1,
            BNN_LUT_1_SIZE,
            &value)) {
        return -2;
    }
    input_q8[1] = value;

    // Feature 2: Subflow Bwd Bytes
    if (!lookup_feature(
            raw_features[2],
            BNN_LUT_2_SHIFT,
            BNN_LUT_2,
            BNN_LUT_2_SIZE,
            &value)) {
        return -2;
    }
    input_q8[2] = value;

    // Feature 3: Total Length of Bwd Packets
    if (!lookup_feature(
            raw_features[3],
            BNN_LUT_3_SHIFT,
            BNN_LUT_3,
            BNN_LUT_3_SIZE,
            &value)) {
        return -2;
    }
    input_q8[3] = value;

    // Feature 4: Destination Port
    if (!lookup_feature(
            raw_features[4],
            BNN_LUT_4_SHIFT,
            BNN_LUT_4,
            BNN_LUT_4_SIZE,
            &value)) {
        return -2;
    }
    input_q8[4] = value;

    // Feature 5: min_seg_size_forward
    if (!lookup_feature(
            raw_features[5],
            BNN_LUT_5_SHIFT,
            BNN_LUT_5,
            BNN_LUT_5_SIZE,
            &value)) {
        return -2;
    }
    input_q8[5] = value;

    // Feature 6: ACK Flag Count
    if (!lookup_feature(
            raw_features[6],
            BNN_LUT_6_SHIFT,
            BNN_LUT_6,
            BNN_LUT_6_SIZE,
            &value)) {
        return -2;
    }
    input_q8[6] = value;

    // Feature 7: Subflow Bwd Packets
    if (!lookup_feature(
            raw_features[7],
            BNN_LUT_7_SHIFT,
            BNN_LUT_7,
            BNN_LUT_7_SIZE,
            &value)) {
        return -2;
    }
    input_q8[7] = value;

    // Feature 8: Fwd Packet Length Max
    if (!lookup_feature(
            raw_features[8],
            BNN_LUT_8_SHIFT,
            BNN_LUT_8,
            BNN_LUT_8_SIZE,
            &value)) {
        return -2;
    }
    input_q8[8] = value;

    // Feature 9: Total Backward Packets
    if (!lookup_feature(
            raw_features[9],
            BNN_LUT_9_SHIFT,
            BNN_LUT_9,
            BNN_LUT_9_SIZE,
            &value)) {
        return -2;
    }
    input_q8[9] = value;

    // Feature 10: Subflow Fwd Bytes
    if (!lookup_feature(
            raw_features[10],
            BNN_LUT_10_SHIFT,
            BNN_LUT_10,
            BNN_LUT_10_SIZE,
            &value)) {
        return -2;
    }
    input_q8[10] = value;

    // Feature 11: Max Packet Length
    if (!lookup_feature(
            raw_features[11],
            BNN_LUT_11_SHIFT,
            BNN_LUT_11,
            BNN_LUT_11_SIZE,
            &value)) {
        return -2;
    }
    input_q8[11] = value;

    // Feature 12: Total Length of Fwd Packets
    if (!lookup_feature(
            raw_features[12],
            BNN_LUT_12_SHIFT,
            BNN_LUT_12,
            BNN_LUT_12_SIZE,
            &value)) {
        return -2;
    }
    input_q8[12] = value;

    // Feature 13: Bwd Header Length
    if (!lookup_feature(
            raw_features[13],
            BNN_LUT_13_SHIFT,
            BNN_LUT_13,
            BNN_LUT_13_SIZE,
            &value)) {
        return -2;
    }
    input_q8[13] = value;

    // Feature 14: Flow Duration
    if (!lookup_feature(
            raw_features[14],
            BNN_LUT_14_SHIFT,
            BNN_LUT_14,
            BNN_LUT_14_SIZE,
            &value)) {
        return -2;
    }
    input_q8[14] = value;

    // Feature 15: Fwd Header Length
    if (!lookup_feature(
            raw_features[15],
            BNN_LUT_15_SHIFT,
            BNN_LUT_15,
            BNN_LUT_15_SIZE,
            &value)) {
        return -2;
    }
    input_q8[15] = value;

    return 0;
}
