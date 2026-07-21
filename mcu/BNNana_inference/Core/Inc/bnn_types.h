#ifndef BNN_TYPES_H
#define BNN_TYPES_H

#include <stdint.h>

typedef struct {
    float destination_port;
    float flow_duration;
    float total_fwd_packets;
    float total_backward_packets;
    float total_len_fwd_packets;
    float total_len_bwd_packets;
    float fwd_packet_length_max;
    float fwd_packet_length_min;
    float fwd_packet_length_mean;
    float bwd_packet_length_max;
    float bwd_packet_length_min;
    float bwd_packet_length_mean;
    float flow_iat_mean;
    float fwd_iat_mean;
    float bwd_iat_mean;
    float min_packet_length;
    float subflow_fwd_bytes;
} FlowFeatures;

typedef union {
    FlowFeatures named;
    float array[17];
} BNN_Input;

#endif