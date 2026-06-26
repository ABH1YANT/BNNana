`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/23/2026 12:59:39 AM
// Design Name: 
// Module Name: tb_hidden_layer
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


`timescale 1ns / 1ps

module tb_hidden_layer();

    parameter INPUT_COUNT = 15;
    parameter NEURON_COUNT = 16;
    parameter INPUT_WIDTH = 8;
    parameter ACC_WIDTH = 16;

    // Inputs
    reg [(INPUT_COUNT * INPUT_WIDTH)-1:0] feature_vector;
    reg [(NEURON_COUNT * INPUT_COUNT)-1:0] all_hidden_weights;
    reg [(NEURON_COUNT * ACC_WIDTH)-1:0] all_hidden_thresholds;

    // Output
    wire [NEURON_COUNT-1:0] hidden_outputs;

    integer i;

    // Instantiate the Unit Under Test (UUT)
    hidden_layer #(
        .INPUT_COUNT(INPUT_COUNT),
        .NEURON_COUNT(NEURON_COUNT),
        .INPUT_WIDTH(INPUT_WIDTH),
        .ACC_WIDTH(ACC_WIDTH)
    ) uut (
        .feature_vector(feature_vector),
        .all_hidden_weights(all_hidden_weights),
        .all_hidden_thresholds(all_hidden_thresholds),
        .hidden_outputs(hidden_outputs)
    );

    initial begin
        // Initialize Inputs
        feature_vector = 0;
        all_hidden_weights = 0;
        all_hidden_thresholds = 0;

        #100;

        // Set all 15 features to a constant value of 10
        for (i = 0; i < INPUT_COUNT; i = i + 1) begin
            feature_vector[i*INPUT_WIDTH +: INPUT_WIDTH] = 8'd10;
        end

        // Set all weights to +1 (Sum for every neuron will be 15 * 10 = 150)
        all_hidden_weights = {(NEURON_COUNT * INPUT_COUNT){1'b1}};

        // ---------------------------------------------------------
        // Test 1: Only Neuron 0 Fires (LSB Test)
        // ---------------------------------------------------------
        // Set all thresholds to 200 (so they fail), except Neuron 0 to 100 (so it fires)
        for (i = 0; i < NEURON_COUNT; i = i + 1) begin
            all_hidden_thresholds[i*ACC_WIDTH +: ACC_WIDTH] = 16'sd200; 
        end
        all_hidden_thresholds[0*ACC_WIDTH +: ACC_WIDTH] = 16'sd100; // Neuron 0 threshold
        
        #10;
        $display("Test 1 (Only N0 fires) : Output=%b | Expected: 0000000000000001", hidden_outputs);

        // ---------------------------------------------------------
        // Test 2: Only Neuron 15 Fires (MSB Test)
        // ---------------------------------------------------------
        for (i = 0; i < NEURON_COUNT; i = i + 1) begin
            all_hidden_thresholds[i*ACC_WIDTH +: ACC_WIDTH] = 16'sd200; 
        end
        all_hidden_thresholds[15*ACC_WIDTH +: ACC_WIDTH] = 16'sd100; // Neuron 15 threshold
        
        #10;
        $display("Test 2 (Only N15 fires): Output=%b | Expected: 1000000000000000", hidden_outputs);

        // ---------------------------------------------------------
        // Test 3: Alternating Neurons Fire (Cross-wiring Test)
        // ---------------------------------------------------------
        for (i = 0; i < NEURON_COUNT; i = i + 1) begin
            if (i % 2 == 0)
                all_hidden_thresholds[i*ACC_WIDTH +: ACC_WIDTH] = 16'sd200; // Even stays quiet
            else
                all_hidden_thresholds[i*ACC_WIDTH +: ACC_WIDTH] = 16'sd100; // Odd fires
        end
        
        #10;
        $display("Test 3 (Alternating)   : Output=%b | Expected: 1010101010101010", hidden_outputs);

        #10;
        $finish;
    end

endmodule
