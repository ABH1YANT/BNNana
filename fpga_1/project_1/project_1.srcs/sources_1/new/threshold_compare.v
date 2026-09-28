`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/14/2026 12:37:01 AM
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
    parameter COUNT_WIDTH = 7
)(
    input  wire [COUNT_WIDTH-1:0] count,
    input  wire [COUNT_WIDTH-1:0] threshold,
    output wire                   output_bit
);

    // BinarySign:
    //
    // count > threshold  -> 1
    // count <= threshold -> 0

    assign output_bit = (count > threshold);

endmodule