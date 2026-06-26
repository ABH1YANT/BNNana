`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/23/2026 01:09:24 AM
// Design Name: 
// Module Name: inference_core
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////



module inference_core #(
    parameter FEATURE_COUNT = 15,       // Updated to 15 features
    parameter HIDDEN_NEURON_COUNT = 16,
    parameter FEATURE_WIDTH = 8,
    parameter ACC_WIDTH = 16
)(
    // Raw Network Traffic
    input wire [(FEATURE_COUNT * FEATURE_WIDTH)-1:0] feature_vector,
    
    // Hidden Layer Parameters
    input wire [(HIDDEN_NEURON_COUNT * FEATURE_COUNT)-1:0] hidden_weights,
    input wire [(HIDDEN_NEURON_COUNT * ACC_WIDTH)-1:0] hidden_thresholds,
    
    // Output Layer Parameters
    input wire [HIDDEN_NEURON_COUNT-1:0] output_weights,
    input wire signed [ACC_WIDTH-1:0] output_threshold,
    
    // Final Result
    output wire classification
);

    // Internal wire connecting Hidden Layer to Output Layer
    wire [HIDDEN_NEURON_COUNT-1:0] hidden_layer_out;

    // Instantiate the Hidden Layer
    hidden_layer #(
        .INPUT_COUNT(FEATURE_COUNT),
        .NEURON_COUNT(HIDDEN_NEURON_COUNT),
        .INPUT_WIDTH(FEATURE_WIDTH),
        .ACC_WIDTH(ACC_WIDTH)
    ) hl_inst (
        .feature_vector(feature_vector),
        .all_hidden_weights(hidden_weights),
        .all_hidden_thresholds(hidden_thresholds),
        .hidden_outputs(hidden_layer_out)
    );

    // Instantiate the Output Layer
    output_layer #(
        .INPUT_COUNT(HIDDEN_NEURON_COUNT),
        .INPUT_WIDTH(1), // Hidden outputs are 1-bit
        .ACC_WIDTH(ACC_WIDTH)
    ) ol_inst (
        .hidden_outputs(hidden_layer_out),
        .output_weights(output_weights),
        .output_threshold(output_threshold),
        .classification(classification)
    );

endmodule
