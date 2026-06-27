`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/22/2026 10:44:40 PM
// Design Name: 
// Module Name: accumulator
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


module accumulator #(
    parameter INPUT_COUNT = 15,
    parameter INPUT_WIDTH = 8,
    parameter ACC_WIDTH = 16
)(
    input wire [(INPUT_COUNT * INPUT_WIDTH)-1:0] feature_values,
    input wire [INPUT_COUNT-1:0] weight_bits,
    output wire signed [ACC_WIDTH-1:0] accumulated_sum
);

    integer i;
    reg signed [ACC_WIDTH-1:0] sum;
    reg [INPUT_WIDTH-1:0] current_feature;

    always @(*) begin
        sum = 0; // Reset sum at the start of the combinational evaluation
        
        for (i = 0; i < INPUT_COUNT; i = i + 1) begin
            // Extract the 8-bit feature for the current index
            // +: is the Verilog indexed part-select operator
            current_feature = feature_values[i*INPUT_WIDTH +: INPUT_WIDTH];
            
            // weight_bits[i] == 1 means +1, == 0 means -1
            if (weight_bits[i] == 1'b1) begin
                // Zero-extend the 8-bit unsigned feature to 16-bits, then add
                sum = sum + $signed({ {(ACC_WIDTH-INPUT_WIDTH){1'b0}}, current_feature });
            end else begin
                // Zero-extend the 8-bit unsigned feature to 16-bits, then subtract
                sum = sum - $signed({ {(ACC_WIDTH-INPUT_WIDTH){1'b0}}, current_feature });
            end
        end
    end

    // Assign the final calculated sum to the output wire
    assign accumulated_sum = sum;

endmodule
