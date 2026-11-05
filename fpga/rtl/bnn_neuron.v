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
    input wire clk,
    input wire rst,
    input wire enable,

    input wire [INPUT_COUNT*INPUT_WIDTH-1:0] inputs,

    input wire [INPUT_COUNT-1:0] weights,

    input wire signed [ACC_WIDTH-1:0] threshold,

    output reg output_bit,
    output reg done
);

    // ============================================================
    // ACCUMULATOR OUTPUT
    // ============================================================

    wire signed [ACC_WIDTH-1:0] sum;
    wire accumulator_done;

    // ============================================================
    // ACCUMULATOR
    // ============================================================

    accumulator #(
        .INPUT_COUNT(INPUT_COUNT),
        .INPUT_WIDTH(INPUT_WIDTH),
        .ACC_WIDTH(ACC_WIDTH)
    ) accumulator_inst (
        .clk(clk),
        .rst(rst),
        .enable(enable),

        .inputs(inputs),
        .weights(weights),

        .sum(sum),
        .done(accumulator_done)
    );


    // ============================================================
    // BATCHNORM + BINARY SIGN
    // ============================================================

    // sum > threshold -> 1
    // sum <= threshold -> 0

    // ============================================================
    // THRESHOLD COMPARISON REGISTER
    // ============================================================

    always @(posedge clk) begin
        if (rst) begin
            output_bit <= 1'b0;
            done       <= 1'b0;
        end
        else begin
            done <= 1'b0;

            if (accumulator_done) begin
                output_bit <= (sum > threshold);
                done       <= 1'b1;
            end
        end
    end
endmodule
