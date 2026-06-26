`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/23/2026 12:51:05 AM
// Design Name: 
// Module Name: tb_bwn_neuron
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


module tb_bwn_neuron();

    // Parameterize to 3 inputs for easy manual math verification
    parameter INPUT_COUNT = 3;
    parameter INPUT_WIDTH = 8;
    parameter ACC_WIDTH = 16;

    // Inputs
    reg [(INPUT_COUNT * INPUT_WIDTH)-1:0] feature_vector;
    reg [INPUT_COUNT-1:0] weight_vector;
    reg signed [ACC_WIDTH-1:0] threshold;

    // Output
    wire neuron_out;

    // Instantiate the Unit Under Test (UUT)
    bwn_neuron #(
        .INPUT_COUNT(INPUT_COUNT),
        .INPUT_WIDTH(INPUT_WIDTH),
        .ACC_WIDTH(ACC_WIDTH)
    ) uut (
        .feature_vector(feature_vector),
        .weight_vector(weight_vector),
        .threshold(threshold),
        .neuron_out(neuron_out)
    );

    initial begin
        // Initialize Inputs
        feature_vector = 0;
        weight_vector = 0;
        threshold = 0;

        // Wait 100 ns for global reset to finish
        #100;

        // Load features: F2 = 30, F1 = 20, F0 = 10
        feature_vector = {8'd30, 8'd20, 8'd10};

        // ---------------------------------------------------------
        // Test Case 1: Neuron Fires (Sum >= Threshold)
        // Weights: All +1 -> Sum = 60
        // Threshold: 50
        // ---------------------------------------------------------
        weight_vector = 3'b111;
        threshold = 16'sd50;
        #10;
        $display("Test 1: Sum=60, Thresh=50 | Output=%b | Expected: 1", neuron_out);

        // ---------------------------------------------------------
        // Test Case 2: Neuron Stays Quiet (Sum < Threshold)
        // Weights: Mixed -> Sum = 0  (-30 + 20 + 10)
        // Threshold: 10
        // ---------------------------------------------------------
        weight_vector = 3'b011;
        threshold = 16'sd10;
        #10;
        $display("Test 2: Sum=0,  Thresh=10 | Output=%b | Expected: 0", neuron_out);

        // ---------------------------------------------------------
        // Test Case 3: Negative Math (Neuron Fires)
        // Weights: All -1 -> Sum = -60
        // Threshold: -70
        // ---------------------------------------------------------
        weight_vector = 3'b000;
        threshold = -16'sd70;
        #10;
        $display("Test 3: Sum=-60, Thresh=-70| Output=%b | Expected: 1", neuron_out);

        // End simulation
        #10;
        $finish;
    end

endmodule
