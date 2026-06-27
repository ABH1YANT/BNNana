`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/23/2026 01:04:48 AM
// Design Name: 
// Module Name: output_layer
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


module output_layer #(
    parameter INPUT_COUNT = 16, // 16 inputs from the hidden layer
    parameter INPUT_WIDTH = 1,  // The inputs are 1-bit binary values
    parameter ACC_WIDTH = 16
)(
    input wire [INPUT_COUNT-1:0] hidden_outputs,
    input wire [INPUT_COUNT-1:0] output_weights,
    input wire signed [ACC_WIDTH-1:0] output_threshold,
    output wire classification
);

    // Instantiate a single Binary Weight Neuron
    bwn_neuron #(
        .INPUT_COUNT(INPUT_COUNT),
        .INPUT_WIDTH(INPUT_WIDTH),
        .ACC_WIDTH(ACC_WIDTH)
    ) out_neuron (
        .feature_vector(hidden_outputs), 
        .weight_vector(output_weights),
        .threshold(output_threshold),
        .neuron_out(classification)
    );

endmodule
