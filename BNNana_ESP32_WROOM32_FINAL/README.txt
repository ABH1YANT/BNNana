BNNana ESP32-WROOM-32 - Final inference + preprocessing
===========================================================

Model:
  16 -> 64 -> 64 -> 32 -> 1
  Dense binary connections
  9,376 binary weights
  BatchNorm fused into thresholds

Input:
  16 raw flow features, in the exact order in selected_features.json /
  artifacts/fpga/feature_order.json.

Preprocessing:
  Each feature uses its supplied feature_luts/*.csv table.
  The LUT metadata specifies upper_bits addressing and the discarded
  lower-bit count. ACK Flag Count uses exact-value addressing.

  The LUT CSV normalized_value is quantized exactly to the model Q1.8
  input convention:
      q = round(normalized_value * 256)
      q = clamp(q, 0, 255)

  The resulting uint8 is interpreted by the model as q / 256.0.

Files:
  BNNana_ESP32.ino     Example raw-flow input and serial output
  bnn_model.h/.cpp     Validated BNN inference engine
  preprocess.h/.cpp    Raw feature -> Q1.8 preprocessing
  preprocess_luts.h    LUT declarations
  preprocess_luts.cpp  Quantized LUT tables in flash
  VALIDATION.txt       BNN validation notes

Arduino IDE:
  Select your ESP32-WROOM-32 board variant (commonly "DOIT ESP32 DEVKIT V1"
  when using a generic ESP32-WROOM-32 module/dev board).
  Open BNNana_ESP32.ino and upload.

IMPORTANT:
  Replace sample_flow with real flow values before using the classifier.
  The project does not capture packets itself; it expects the 16 extracted
  flow features as input.
