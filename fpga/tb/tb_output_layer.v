`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/23/2026 01:05:39 AM
// Design Name: 
// Module Name: tb_output_layer
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


module tb_output_layer();

    parameter INPUT_COUNT = 16;
    parameter INPUT_WIDTH = 1;
    parameter ACC_WIDTH = 16;

    // Inputs
    reg [INPUT_COUNT-1:0] hidden_outputs;
    reg [INPUT_COUNT-1:0] output_weights;
    reg signed [ACC_WIDTH-1:0] output_threshold;

    // Output
    wire classification;

    // Instantiate the Unit Under Test (UUT)
    output_layer #(
        .INPUT_COUNT(INPUT_COUNT),
        .INPUT_WIDTH(INPUT_WIDTH),
        .ACC_WIDTH(ACC_WIDTH)
    ) uut (
        .hidden_outputs(hidden_outputs),
        .output_weights(output_weights),
        .output_threshold(output_threshold),
        .classification(classification)
    );

    initial begin
        // Initialize Inputs
        hidden_outputs = 0;
        output_weights = 0;
        output_threshold = 0;

        #100;

        // ---------------------------------------------------------
        // Test 1: Strong DDoS (Sum = 16, Threshold = 10)
        // ---------------------------------------------------------
        hidden_outputs = 16'hFFFF; // All 16 neurons fired (1111111111111111)
        output_weights = 16'hFFFF; // All weights are +1
        output_threshold = 16'sd10;
        
        #10;
        $display("Test 1 (Strong DDoS) : Output=%b | Expected: 1", classification);

        // ---------------------------------------------------------
        // Test 2: Benign Traffic (Sum = 8, Threshold = 10)
        // ---------------------------------------------------------
        hidden_outputs = 16'h00FF; // Only 8 neurons fired (0000000011111111)
        output_weights = 16'hFFFF; // All weights are +1
        output_threshold = 16'sd10;
        
        #10;
        $display("Test 2 (Benign)      : Output=%b | Expected: 0", classification);

        // ---------------------------------------------------------
        // Test 3: Negative Weights (Sum = -16, Threshold = -20)
        // ---------------------------------------------------------
        hidden_outputs = 16'hFFFF; // All 16 neurons fired
        output_weights = 16'h0000; // All weights are -1
        output_threshold = -16'sd20;
        
        #10;
        $display("Test 3 (Negative W)  : Output=%b | Expected: 1", classification);

        #10;
        $finish;
    end

endmodule
