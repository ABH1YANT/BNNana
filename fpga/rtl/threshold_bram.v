`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/26/2026 01:43:23 AM
// Design Name: 
// Module Name: threshold_bram
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


module threshold_bram #(
    parameter NEURON_COUNT = 16,
    parameter ACC_WIDTH = 16
)(
    // Output to Neural Network (Inference Core)
    output wire [(NEURON_COUNT * ACC_WIDTH)-1:0] all_thresholds
);

    // 2D Array representing the memory (16 rows, 16 bits per row)
    reg [ACC_WIDTH-1:0] mem [0:NEURON_COUNT-1];

    // Load the memory file when the FPGA powers on
    initial begin
        $readmemb("thresholds.mem", mem);
    end

    // Flatten the 2D memory array into a single 1D wire
    genvar i;
    generate
        for (i = 0; i < NEURON_COUNT; i = i + 1) begin : flatten_thresholds
            assign all_thresholds[i * ACC_WIDTH +: ACC_WIDTH] = mem[i];
        end
    endgenerate

endmodule