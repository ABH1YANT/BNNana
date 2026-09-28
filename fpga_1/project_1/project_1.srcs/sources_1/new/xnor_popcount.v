`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/14/2026 12:20:16 AM
// Design Name: 
// Module Name: xnor_popcount
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
module xnor_popcount #(
    parameter WIDTH = 64
)(
    input  wire [WIDTH-1:0] inputs,
    input  wire [WIDTH-1:0] weights,

    // XNOR result:
    // 1 = input and weight match
    // 0 = input and weight differ
    output wire [WIDTH-1:0] matches,

    // Number of matching bits
    // Range: 0 to 64
    output reg [6:0] count
);

    integer i;

    // ============================================================
    // XNOR
    // ============================================================

    assign matches = ~(inputs ^ weights);


    // ============================================================
    // POPCOUNT
    // ============================================================

    always @(*) begin

        count = 7'd0;

        for (i = 0; i < WIDTH; i = i + 1) begin
            count = count + matches[i];
        end

    end

endmodule