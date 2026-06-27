`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/23/2026 12:49:59 AM
// Design Name: 
// Module Name: bwn_neuron
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

module bwn_neuron #(
    parameter INPUT_COUNT = 15,  // Updated to 15 based on your dataset
    parameter INPUT_WIDTH = 8,
    parameter ACC_WIDTH = 16
)(
    input wire [(INPUT_COUNT * INPUT_WIDTH)-1:0] feature_vector,
    input wire [INPUT_COUNT-1:0] weight_vector,
    input wire signed [ACC_WIDTH-1:0] threshold,
    output wire neuron_out
);

    // Internal wire connecting the accumulator to the comparator
    wire signed [ACC_WIDTH-1:0] acc_sum;

    // Instantiate the Accumulator
    accumulator #(
        .INPUT_COUNT(INPUT_COUNT),
        .INPUT_WIDTH(INPUT_WIDTH),
        .ACC_WIDTH(ACC_WIDTH)
    ) acc_inst (
        .feature_values(feature_vector),
        .weight_bits(weight_vector),
        .accumulated_sum(acc_sum)
    );

    // Instantiate the Threshold Comparator
    threshold_compare #(
        .ACC_WIDTH(ACC_WIDTH)
    ) comp_inst (
        .accumulated_sum(acc_sum),
        .threshold(threshold),
        .neuron_output(neuron_out)
    );

endmodule
