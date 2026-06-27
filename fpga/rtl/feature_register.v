`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/26/2026 01:35:27 AM
// Design Name: 
// Module Name: feature_register
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


module feature_register #(
    parameter FEATURE_COUNT = 15,
    parameter FEATURE_WIDTH = 8
)(
    input wire clk,
    input wire rst,
    
    // Input from Packet Parser
    input wire [(FEATURE_COUNT * FEATURE_WIDTH)-1:0] feature_vector,
    input wire load_enable,
    
    // Output to Neural Network (Inference Core)
    output wire [(FEATURE_COUNT * FEATURE_WIDTH)-1:0] registered_features
);

    // The massive 120-bit internal memory register
    reg [(FEATURE_COUNT * FEATURE_WIDTH)-1:0] data_reg;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            // Clear the register on reset
            data_reg <= 0;
        end else if (load_enable == 1'b1) begin
            // Only update the register when the packet parser says the data is valid
            data_reg <= feature_vector;
        end
        // If load_enable is 0, it automatically holds its current value
    end

    // Connect the internal register to the output wire
    assign registered_features = data_reg;

endmodule
