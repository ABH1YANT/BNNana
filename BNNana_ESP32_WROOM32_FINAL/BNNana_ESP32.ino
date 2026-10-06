#include <Arduino.h>
#include "bnn_model.h"
#include "preprocess.h"

// Replace these 16 raw values with the features from one network flow.
// Field order is defined by artifacts/fpga/feature_order.json.
static RawFlowFeatures sample_flow = {
    0,      // Bwd Packet Length Max
    0,      // Min Packet Length
    0,      // Subflow Bwd Bytes
    0,      // Total Length of Bwd Packets
    0,      // Destination Port
    0,      // min_seg_size_forward
    0,      // ACK Flag Count
    0,      // Subflow Bwd Packets
    0,      // Fwd Packet Length Max
    0,      // Total Backward Packets
    0,      // Subflow Fwd Bytes
    0,      // Max Packet Length
    0,      // Total Length of Fwd Packets
    0,      // Bwd Header Length
    0,      // Flow Duration
    0       // Fwd Header Length
};

void setup()
{
    Serial.begin(115200);
    delay(500);

    uint8_t x_q8[BNN_INPUTS];
    preprocess_flow(sample_flow, x_q8);

    Serial.println("BNNana ESP32-WROOM-32");
    Serial.println("Preprocessed Q1.8 input:");

    for (int i = 0; i < BNN_INPUTS; ++i) {
        Serial.print(x_q8[i]);
        if (i + 1 < BNN_INPUTS) Serial.print(", ");
    }
    Serial.println();

    uint32_t t0 = micros();
    uint8_t result = bnn_predict_q8(x_q8);
    uint32_t dt = micros() - t0;

    Serial.print("Prediction: ");
    Serial.println(result);

    Serial.print("Inference time (us): ");
    Serial.println(dt);

    uint32_t t1 = micros();
    (void)bnn_predict_raw(sample_flow);
    uint32_t total_dt = micros() - t1;

    Serial.print("Preprocess + inference (us): ");
    Serial.println(total_dt);
}

void loop()
{
}
