`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/22/2026 11:18:02 PM
// Design Name: 
// Module Name: threshold_compare
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


module threshold_compare #(
    parameter ACC_WIDTH = 16
)(
    input wire signed [ACC_WIDTH-1:0] accumulated_sum,
    input wire signed [ACC_WIDTH-1:0] threshold,
    output wire neuron_output
);

    // Combinational logic: If sum is greater than or equal to threshold, output 1. Else 0.
    assign neuron_output = (accumulated_sum >= threshold) ? 1'b1 : 1'b0;

endmodule
