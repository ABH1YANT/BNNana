// Generated: 2026-07-21 22:53:43
#ifndef BNN_TYPES_H
#define BNN_TYPES_H

#include <stdint.h>

typedef struct {
    float destination_port;
    float bwd_header_length;
    float total_backward_packets;
    float min_packet_length;
    float subflow_fwd_bytes;
    float max_packet_length;
    float flow_duration;
    float fwd_packet_length_max;
    float bwd_packet_length_max;
    float min_seg_size_forward;
    float fwd_header_length;
    float psh_flag_count;
    float urg_flag_count;
    float syn_flag_count;
    float ack_flag_count;
    float fin_flag_count;
    float rst_flag_count;
} FlowFeatures;

typedef union {
    FlowFeatures named;
    float array[17];
} BNN_Input;

#endif