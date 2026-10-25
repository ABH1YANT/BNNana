
#include "bnn_model.h"
#include "bnn_params.h"

#include <math.h>
#include <stddef.h>
#include <stdint.h>

// Convert a floating-point value to a binary activation.
// Matches ste.py: sign(x), with zero mapped to +1.
static inline int8_t binary_sign(float x)
{
    return (x >= 0.0f) ? 1 : -1;
}

// Calculate BatchNorm for one neuron in evaluation mode.
static inline float batch_norm(
    float value,
    float gamma,
    float beta,
    float running_mean,
    float running_var)
{
    return gamma * ((value - running_mean) /
        sqrtf(running_var + BN_EPS)) + beta;
}

// First hidden layer:
// 16 quantized input features -> 64 binary activations.
static void layer0_forward(
    const int16_t input_q8[BNN_INPUT_SIZE],
    int8_t output[HIDDEN1_SIZE])
{
    for (int neuron = 0; neuron < HIDDEN1_SIZE; ++neuron)
    {
        float sum = 0.0f;

        for (int i = 0; i < INPUT_SIZE; ++i)
        {
            // Q1.8 input integer represents value / 256.
            const float x = (float)input_q8[i] / 256.0f;

            const int8_t weight =
                LAYER0_WEIGHTS[neuron * INPUT_SIZE + i];

            sum += (weight > 0) ? x : -x;
        }

        const float normalized = batch_norm(
            sum,
            LAYER0_BN_GAMMA[neuron],
            LAYER0_BN_BETA[neuron],
            LAYER0_BN_RUNNING_MEAN[neuron],
            LAYER0_BN_RUNNING_VAR[neuron]);

        output[neuron] = binary_sign(normalized);
    }
}

// Second hidden layer:
// Concatenated input from hidden layers 0 and 1.
static void layer1_forward(
    const int8_t input[HIDDEN1_SIZE],
    int8_t output[HIDDEN2_SIZE])
{
    for (int neuron = 0; neuron < HIDDEN2_SIZE; ++neuron)
    {
        int32_t sum = 0;

        for (int i = 0; i < HIDDEN1_SIZE; ++i)
        {
            const int8_t weight =
                LAYER1_WEIGHTS[neuron * HIDDEN1_SIZE + i];

            sum += (weight == input[i]) ? 1 : -1;
        }

        const float normalized = batch_norm(
            (float)sum,
            LAYER1_BN_GAMMA[neuron],
            LAYER1_BN_BETA[neuron],
            LAYER1_BN_RUNNING_MEAN[neuron],
            LAYER1_BN_RUNNING_VAR[neuron]);

        output[neuron] = binary_sign(normalized);
    }
}

// Third hidden layer:
// Concatenated outputs from hidden layers 0, 1 and 2.
// Its input length is 64 + 64 = 128.
static void layer2_forward(
    const int8_t input[HIDDEN1_SIZE + HIDDEN2_SIZE],
    int8_t output[HIDDEN3_SIZE])
{
    constexpr int LAYER_INPUT_SIZE =
        HIDDEN1_SIZE + HIDDEN2_SIZE;

    for (int neuron = 0; neuron < HIDDEN3_SIZE; ++neuron)
    {
        int32_t sum = 0;

        for (int i = 0; i < LAYER_INPUT_SIZE; ++i)
        {
            const int8_t weight =
                LAYER2_WEIGHTS[neuron * LAYER_INPUT_SIZE + i];

            sum += (weight == input[i]) ? 1 : -1;
        }

        const float normalized = batch_norm(
            (float)sum,
            LAYER2_BN_GAMMA[neuron],
            LAYER2_BN_BETA[neuron],
            LAYER2_BN_RUNNING_MEAN[neuron],
            LAYER2_BN_RUNNING_VAR[neuron]);

        output[neuron] = binary_sign(normalized);
    }
}

// Output layer:
// Concatenated hidden activations: 64 + 64 + 32 = 160.
static float output_forward(
    const int8_t input[
        HIDDEN1_SIZE + HIDDEN2_SIZE + HIDDEN3_SIZE])
{
    constexpr int OUTPUT_INPUT_SIZE =
        HIDDEN1_SIZE + HIDDEN2_SIZE + HIDDEN3_SIZE;

    int32_t logit = 0;

    for (int i = 0; i < OUTPUT_INPUT_SIZE; ++i)
    {
        const int8_t weight = OUTPUT_WEIGHTS[i];

        logit += (weight == input[i]) ? 1 : -1;
    }

    return (float)logit;
}

// Public inference function declared in bnn_model.h.
extern "C" int8_t bnn_predict(
    const int16_t input_q8[BNN_INPUT_SIZE])
{
    if (input_q8 == nullptr)
    {
        return -1;
    }

    int8_t hidden0[HIDDEN1_SIZE];
    int8_t hidden1[HIDDEN2_SIZE];
    int8_t hidden2[HIDDEN3_SIZE];

    int8_t dense_input1[HIDDEN1_SIZE];
    int8_t dense_input2[
        HIDDEN1_SIZE + HIDDEN2_SIZE];
    int8_t dense_input3[
        HIDDEN1_SIZE + HIDDEN2_SIZE + HIDDEN3_SIZE];

    // Hidden layer 0.
    layer0_forward(input_q8, hidden0);

    // Hidden layer 1 receives hidden0.
    for (int i = 0; i < HIDDEN1_SIZE; ++i)
    {
        dense_input1[i] = hidden0[i];
    }

    layer1_forward(dense_input1, hidden1);

    // Hidden layer 2 receives hidden0 concatenated with hidden1.
    for (int i = 0; i < HIDDEN1_SIZE; ++i)
    {
        dense_input2[i] = hidden0[i];
    }

    for (int i = 0; i < HIDDEN2_SIZE; ++i)
    {
        dense_input2[HIDDEN1_SIZE + i] = hidden1[i];
    }

    layer2_forward(dense_input2, hidden2);

    // Final output receives hidden0 + hidden1 + hidden2.
    for (int i = 0; i < HIDDEN1_SIZE; ++i)
    {
        dense_input3[i] = hidden0[i];
    }

    for (int i = 0; i < HIDDEN2_SIZE; ++i)
    {
        dense_input3[HIDDEN1_SIZE + i] = hidden1[i];
    }

    for (int i = 0; i < HIDDEN3_SIZE; ++i)
    {
        dense_input3[HIDDEN1_SIZE + HIDDEN2_SIZE + i] =
            hidden2[i];
    }

    const float logit = output_forward(dense_input3);

    // BCEWithLogits classification threshold.
    return (logit >= 0.0f) ? 1 : 0;
}
