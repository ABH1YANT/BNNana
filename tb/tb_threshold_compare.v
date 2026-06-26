`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/22/2026 11:19:22 PM
// Design Name: 
// Module Name: tb_threshold_compare
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


module tb_threshold_compare();

    parameter ACC_WIDTH = 16;

    // Inputs
    reg signed [ACC_WIDTH-1:0] accumulated_sum;
    reg signed [ACC_WIDTH-1:0] threshold;

    // Output
    wire neuron_output;

    // Instantiate the Unit Under Test (UUT)
    threshold_compare #(
        .ACC_WIDTH(ACC_WIDTH)
    ) uut (
        .accumulated_sum(accumulated_sum),
        .threshold(threshold),
        .neuron_output(neuron_output)
    );

    initial begin
        // Initialize Inputs
        accumulated_sum = 0;
        threshold = 0;

        // Wait 100 ns for global reset to finish
        #100;

        // ---------------------------------------------------------
        // Test Case 1: Sum > Threshold
        // ---------------------------------------------------------
        accumulated_sum = 16'sd15;  // 'sd' means signed decimal
        threshold       = 16'sd10;
        #10;
        $display("Test 1 (Sum > Thresh) : Sum=%0d, Thresh=%0d | Output=%b | Expected: 1", accumulated_sum, threshold, neuron_output);

        // ---------------------------------------------------------
        // Test Case 2: Sum == Threshold (Crucial Boundary)
        // ---------------------------------------------------------
        accumulated_sum = 16'sd10;
        threshold       = 16'sd10;
        #10;
        $display("Test 2 (Sum == Thresh): Sum=%0d, Thresh=%0d | Output=%b | Expected: 1", accumulated_sum, threshold, neuron_output);

        // ---------------------------------------------------------
        // Test Case 3: Sum < Threshold
        // ---------------------------------------------------------
        accumulated_sum = 16'sd5;
        threshold       = 16'sd10;
        #10;
        $display("Test 3 (Sum < Thresh) : Sum=%0d, Thresh=%0d  | Output=%b | Expected: 0", accumulated_sum, threshold, neuron_output);

        // ---------------------------------------------------------
        // Test Case 4: Negative Numbers (Sum > Threshold)
        // -5 is mathematically greater than -10
        // ---------------------------------------------------------
        accumulated_sum = -16'sd5;
        threshold       = -16'sd10;
        #10;
        $display("Test 4 (Negative >)   : Sum=%0d, Thresh=%0d | Output=%b | Expected: 1", accumulated_sum, threshold, neuron_output);

        // ---------------------------------------------------------
        // Test Case 5: Negative Numbers (Sum < Threshold)
        // -15 is mathematically less than -10
        // ---------------------------------------------------------
        accumulated_sum = -16'sd15;
        threshold       = -16'sd10;
        #10;
        $display("Test 5 (Negative <)   : Sum=%0d, Thresh=%0d | Output=%b | Expected: 0", accumulated_sum, threshold, neuron_output);

        // End simulation
        #10;
        $finish;
    end

endmodule
