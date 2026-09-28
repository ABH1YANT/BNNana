`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/27/2026 12:47:10 PM
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

`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// BNNana
// Output Layer
//
// Architecture:
//     160 binary inputs -> 1 binary output
//
// Inputs:
//     Layer 0 = 64 bits
//     Layer 1 = 64 bits
//     Layer 2 = 32 bits
//
//     Total = 160 bits
//
// Operation:
//     Fixed-weight XNOR
//     -> 160-bit match vector
//     -> popcount
//     -> threshold
//     -> 1-bit output
//
// Weight:
//     160-bit HARDWARE CONSTANT
//
// Threshold:
//     81
//
// No BRAM is used for weights or threshold.
//////////////////////////////////////////////////////////////////////////////////

module output_layer #(
    parameter INPUT_COUNT = 160
)(
    input  wire [INPUT_COUNT-1:0] inputs,
    output wire                   output_bit
);

    // ============================================================
    // ACTUAL TRAINED OUTPUT WEIGHTS
    // ============================================================

    wire [159:0] weights;

    assign weights =
        160'hF3E67C70AD428AFAB34FCC616F3069A5399D4F3F;


    // ============================================================
    // ACTUAL TRAINED OUTPUT THRESHOLD
    //
    // Popcount range = 0..160
    // Threshold = 81
    // ============================================================

    wire [7:0] threshold;

    assign threshold = 8'd81;


    // ============================================================
    // FIXED-WEIGHT XNOR
    //
    // weight = 1 -> input
    // weight = 0 -> inverted input
    //
    // Since weights are constants, synthesis can optimize this
    // into direct wires/inverters.
    // ============================================================

    wire [159:0] match_bits;

    assign match_bits = ~(inputs ^ weights);


    // ============================================================
    // 160-BIT POPCOUNT
    //
    // Result range = 0..160
    // Therefore 8 bits are sufficient.
    // ============================================================

    reg [7:0] match_count;

    integer i;

    always @(*) begin

        match_count = 8'd0;

        for (i = 0; i < INPUT_COUNT; i = i + 1) begin

            match_count =
                match_count
                +
                match_bits[i];

        end

    end


    // ============================================================
    // FINAL BINARY SIGN / THRESHOLD
    //
    // count > 81  -> 1
    // count <= 81 -> 0
    // ============================================================

    assign output_bit = (match_count > threshold);

endmodule
