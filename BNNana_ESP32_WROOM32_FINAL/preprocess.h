#pragma once
#include <Arduino.h>
#include <stdint.h>

#include "bnn_model.h"

struct RawFlowFeatures {
    uint32_t bwd_packet_length_max;
    uint32_t min_packet_length;
    uint32_t subflow_bwd_bytes;
    uint32_t total_length_bwd_packets;
    uint32_t destination_port;
    uint32_t min_seg_size_forward;
    uint32_t ack_flag_count;
    uint32_t subflow_bwd_packets;
    uint32_t fwd_packet_length_max;
    uint32_t total_backward_packets;
    uint32_t subflow_fwd_bytes;
    uint32_t max_packet_length;
    uint32_t total_length_fwd_packets;
    uint32_t bwd_header_length;
    uint32_t flow_duration;
    uint32_t fwd_header_length;
};

// Converts one raw flow into the exact 16-byte Q1.8 input expected by the BNN.
// LUT addressing follows lut_metadata.json: upper_bits, i.e. raw >> discarded_lower_bits.
// ACK Flag Count uses exact_value addressing.
void preprocess_flow(const RawFlowFeatures& raw, uint8_t x_q8[BNN_INPUTS]);

// Convenience wrapper: preprocess + BNN inference.
uint8_t bnn_predict_raw(const RawFlowFeatures& raw);
