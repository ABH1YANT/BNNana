`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/26/2026 01:44:15 AM
// Design Name: 
// Module Name: tb_weight_bram
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


module tb_weight_bram();

    parameter NEURON_COUNT = 16;
    parameter INPUT_COUNT = 15;
    parameter ACC_WIDTH = 16;

    wire [(NEURON_COUNT * INPUT_COUNT)-1:0] all_weights;
    wire [(NEURON_COUNT * ACC_WIDTH)-1:0] all_thresholds;

    // Instantiate the Weight BRAM
    weight_bram #(
        .NEURON_COUNT(NEURON_COUNT),
        .INPUT_COUNT(INPUT_COUNT)
    ) w_bram (
        .all_weights(all_weights)
    );

    // Instantiate the Threshold BRAM
    threshold_bram #(
        .NEURON_COUNT(NEURON_COUNT),
        .ACC_WIDTH(ACC_WIDTH)
    ) t_bram (
        .all_thresholds(all_thresholds)
    );

    initial begin
        $display("--- Starting BRAM Initialization Test ---");

        // Wait a moment for the hardware to read the physical .mem files
        #10;

        // Verify the flattened outputs
        $display("Checking Flattened Weights Bus:");
        $display("%b", all_weights);

        $display("Checking Flattened Thresholds Bus:");
        $display("%b", all_thresholds);

        #10;
        $display("--- Simulation Complete ---");
        $finish;
    end

endmodule
