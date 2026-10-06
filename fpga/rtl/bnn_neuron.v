`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/13/2026 10:34:38 PM
// Design Name: 
// Module Name: bnn_neuron
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
module bnn_neuron #(
    parameter INPUT_COUNT = 16,
    parameter INPUT_WIDTH = 8,
    parameter ACC_WIDTH   = 16
)(
    input wire [INPUT_COUNT*INPUT_WIDTH-1:0] inputs,

    // Binary weights:
    // 1 = +1
    // 0 = -1
    input wire [INPUT_COUNT-1:0] weights,

    // BatchNorm-derived signed threshold
    input wire signed [ACC_WIDTH-1:0] threshold,

    // BinarySign output:
    // 1 = +1
    // 0 = -1
    output wire output_bit
);

    // ============================================================
    // ACCUMULATOR OUTPUT
    // ============================================================

    wire signed [ACC_WIDTH-1:0] sum;


    // ============================================================
    // ACCUMULATOR
    // ============================================================

    accumulator #(
        .INPUT_COUNT(INPUT_COUNT),
        .INPUT_WIDTH(INPUT_WIDTH),
        .ACC_WIDTH(ACC_WIDTH)
    ) accumulator_inst (

        .inputs(inputs),
        .weights(weights),
        .sum(sum)

    );


    // ============================================================
    // BATCHNORM + BINARY SIGN
    // ============================================================

    // sum > threshold -> 1
    // sum <= threshold -> 0

    assign output_bit = (sum > threshold);

endmodule
