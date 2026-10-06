#pragma once
#include <Arduino.h>
#include <stdint.h>

// LUT entries are already quantized to the model's Q1.8 uint8 input.
// normalized_value -> round(normalized_value * 256), clipped to 255.
// Tables are stored in flash via PROGMEM.
//
// Generated from the project's feature_luts CSV files.

extern const uint8_t LUT_BWD_PACKET_LENGTH_MAX[4096] PROGMEM;
extern const uint8_t LUT_MIN_PACKET_LENGTH[1024] PROGMEM;
extern const uint8_t LUT_SUBFLOW_BWD_BYTES[65536] PROGMEM;
extern const uint8_t LUT_TOTAL_LENGTH_OF_BWD_PACKETS[65536] PROGMEM;
extern const uint8_t LUT_DESTINATION_PORT[4096] PROGMEM;
extern const uint8_t LUT_MIN_SEG_SIZE_FORWARD[1024] PROGMEM;
extern const uint8_t LUT_ACK_FLAG_COUNT[2] PROGMEM;
extern const uint8_t LUT_SUBFLOW_BWD_PACKETS[4096] PROGMEM;
extern const uint8_t LUT_FWD_PACKET_LENGTH_MAX[4096] PROGMEM;
extern const uint8_t LUT_TOTAL_BACKWARD_PACKETS[4096] PROGMEM;
extern const uint8_t LUT_SUBFLOW_FWD_BYTES[65536] PROGMEM;
extern const uint8_t LUT_MAX_PACKET_LENGTH[4096] PROGMEM;
extern const uint8_t LUT_TOTAL_LENGTH_OF_FWD_PACKETS[65536] PROGMEM;
extern const uint8_t LUT_BWD_HEADER_LENGTH[65536] PROGMEM;
extern const uint8_t LUT_FLOW_DURATION[65536] PROGMEM;
extern const uint8_t LUT_FWD_HEADER_LENGTH[65536] PROGMEM;
