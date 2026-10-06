#include "preprocess.h"
#include "preprocess_luts.h"
#include <pgmspace.h>

static inline uint16_t upper_bits_bucket(uint32_t raw, uint8_t discarded, uint16_t bucket_count)
{
    uint32_t idx = (discarded == 0) ? raw : (raw >> discarded);
    if (idx >= bucket_count) idx = bucket_count - 1;
    return (uint16_t)idx;
}

static inline uint8_t lut_value(const uint8_t* table, uint16_t idx)
{
    return pgm_read_byte(&table[idx]);
}

static inline uint8_t lut_upper(const uint8_t* table, uint32_t raw,
                                uint8_t discarded, uint16_t bucket_count)
{
    return lut_value(table, upper_bits_bucket(raw, discarded, bucket_count));
}

void preprocess_flow(const RawFlowFeatures& r, uint8_t x[BNN_INPUTS])
{
    x[0] = lut_upper(LUT_BWD_PACKET_LENGTH_MAX, r.bwd_packet_length_max, 2, 4096);
    x[1] = lut_upper(LUT_MIN_PACKET_LENGTH, r.min_packet_length, 1, 1024);
    x[2] = lut_upper(LUT_SUBFLOW_BWD_BYTES, r.subflow_bwd_bytes, 9, 65536);
    x[3] = lut_upper(LUT_TOTAL_LENGTH_OF_BWD_PACKETS, r.total_length_bwd_packets, 9, 65536);
    x[4] = lut_upper(LUT_DESTINATION_PORT, r.destination_port, 4, 4096);
    x[5] = lut_upper(LUT_MIN_SEG_SIZE_FORWARD, r.min_seg_size_forward, 1, 1024);
    x[6] = lut_value(LUT_ACK_FLAG_COUNT, (uint16_t)(r.ack_flag_count > 0 ? 1 : 0));
    x[7] = lut_upper(LUT_SUBFLOW_BWD_PACKETS, r.subflow_bwd_packets, 5, 4096);
    x[8] = lut_upper(LUT_FWD_PACKET_LENGTH_MAX, r.fwd_packet_length_max, 3, 4096);
    x[9] = lut_upper(LUT_TOTAL_BACKWARD_PACKETS, r.total_backward_packets, 5, 4096);
    x[10] = lut_upper(LUT_SUBFLOW_FWD_BYTES, r.subflow_fwd_bytes, 5, 65536);
    x[11] = lut_upper(LUT_MAX_PACKET_LENGTH, r.max_packet_length, 3, 4096);
    x[12] = lut_upper(LUT_TOTAL_LENGTH_OF_FWD_PACKETS, r.total_length_fwd_packets, 5, 65536);
    x[13] = lut_upper(LUT_BWD_HEADER_LENGTH, r.bwd_header_length, 5, 65536);
    x[14] = lut_upper(LUT_FLOW_DURATION, r.flow_duration, 11, 65536);
    x[15] = lut_upper(LUT_FWD_HEADER_LENGTH, r.fwd_header_length, 5, 65536);
}

uint8_t bnn_predict_raw(const RawFlowFeatures& raw)
{
    uint8_t x[BNN_INPUTS];
    preprocess_flow(raw, x);
    return bnn_predict_q8(x);
}
