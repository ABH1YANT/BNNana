
#include <Arduino.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "bnn_model.h"
#include "bnn_preprocess.h"

static constexpr uint32_t SERIAL_BAUD = 115200;
static constexpr size_t FEATURE_COUNT = BNN_FEATURE_COUNT;
static constexpr size_t LINE_BUFFER_SIZE = 256;

static char line_buffer[LINE_BUFFER_SIZE];
static size_t line_length = 0;

// Parse 16 comma-separated unsigned integers.
static bool parse_features(
    const char* line,
    uint32_t features[FEATURE_COUNT])
{
    if (line == nullptr) {
        return false;
    }

    char buffer[LINE_BUFFER_SIZE];
    strncpy(buffer, line, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';

    char* token = strtok(buffer, ",");
    size_t count = 0;

    while (token != nullptr && count < FEATURE_COUNT) {
        char* end = nullptr;
        unsigned long value = strtoul(token, &end, 10);

        // Reject empty, malformed, negative, or overflowing values.
        if (token == end || *end != '\0' || token[0] == '-') {
            return false;
        }

        if (value > UINT32_MAX) {
            return false;
        }

        features[count++] = static_cast<uint32_t>(value);
        token = strtok(nullptr, ",");
    }

    // Exactly 16 values are required.
    return count == FEATURE_COUNT && token == nullptr;
}

static void process_line(const char* line)
{
    uint32_t raw[FEATURE_COUNT];
    int16_t input_q8[FEATURE_COUNT];

    if (!parse_features(line, raw)) {
        Serial.println("ERR,PARSE");
        return;
    }

    int8_t status = bnn_preprocess(raw, input_q8);

    if (status != 0) {
        Serial.println("ERR,PREPROCESS");
        return;
    }

    int8_t prediction = bnn_predict(input_q8);

    if (prediction != 0 && prediction != 1) {
        Serial.println("ERR,INFERENCE");
        return;
    }

    Serial.print("PRED,");
    Serial.println(static_cast<int>(prediction));
}

void setup()
{
    Serial.begin(SERIAL_BAUD);
    line_length = 0;

    // Startup message lets the PC know the firmware is running.
    Serial.println("BNNANA_READY");
}

void loop()
{
    while (Serial.available() > 0) {
        char c = static_cast<char>(Serial.read());

        if (c == '\r') {
            continue;
        }

        if (c == '\n') {
            line_buffer[line_length] = '\0';

            if (line_length > 0) {
                process_line(line_buffer);
            }

            line_length = 0;
            continue;
        }

        if (line_length < LINE_BUFFER_SIZE - 1) {
            line_buffer[line_length++] = c;
        } else {
            line_length = 0;
            Serial.println("ERR,LINE_TOO_LONG");
        }
    }
}
