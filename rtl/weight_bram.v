`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/26/2026 01:42:45 AM
// Design Name: 
// Module Name: weight_bram
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


module weight_bram #(
    parameter NEURON_COUNT = 16,
    parameter INPUT_COUNT = 15
)(
    // Output to Neural Network (Inference Core)
    output wire [(NEURON_COUNT * INPUT_COUNT)-1:0] all_weights
);

    // 2D Array representing the memory (16 rows, 15 bits per row)
    reg [INPUT_COUNT-1:0] mem [0:NEURON_COUNT-1];

    // Load the memory file when the FPGA powers on
    initial begin
        $readmemb("weights.mem", mem);
    end

    // Flatten the 2D memory array into a single 1D wire
    genvar i;
    generate
        for (i = 0; i < NEURON_COUNT; i = i + 1) begin : flatten_weights
            assign all_weights[i * INPUT_COUNT +: INPUT_COUNT] = mem[i];
        end
    endgenerate

endmodule
