`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/23/2026 01:10:44 AM
// Design Name: 
// Module Name: tb_inference_core
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



module tb_inference_core();
    
    parameter FEATURE_COUNT = 15;
    parameter HIDDEN_NEURON_COUNT = 16;
    parameter FEATURE_WIDTH = 8;
    parameter ACC_WIDTH = 16;

    // Inputs
    reg [(FEATURE_COUNT * FEATURE_WIDTH)-1:0] features;
    reg [(HIDDEN_NEURON_COUNT * FEATURE_COUNT)-1:0] h_weights;
    reg [(HIDDEN_NEURON_COUNT * ACC_WIDTH)-1:0] h_thresholds;
    reg [HIDDEN_NEURON_COUNT-1:0] o_weights;
    reg signed [ACC_WIDTH-1:0] o_threshold;
    
    // Output
    wire classification;

    // Instantiate the Unit Under Test (UUT)
    inference_core #(
        .FEATURE_COUNT(FEATURE_COUNT),
        .HIDDEN_NEURON_COUNT(HIDDEN_NEURON_COUNT),
        .FEATURE_WIDTH(FEATURE_WIDTH),
        .ACC_WIDTH(ACC_WIDTH)
    ) uut (
        .feature_vector(features),
        .hidden_weights(h_weights),
        .hidden_thresholds(h_thresholds),
        .output_weights(o_weights),
        .output_threshold(o_threshold),
        .classification(classification)
    );

    initial begin
        // Initialize everything to 0 to prevent X (unknown) states
        features = 0;
        h_weights = 0;
        h_thresholds = 0;
        o_weights = 0;
        o_threshold = 0;

        #100;

        // ---------------------------------------------------------
        // End-to-End Test: Force a DDoS Detection
        // ---------------------------------------------------------
        
        // 1. Set all 15 features to 1
        features = {15{8'd1}}; 
        
        // 2. Set all hidden weights to +1
        h_weights = {(HIDDEN_NEURON_COUNT * FEATURE_COUNT){1'b1}}; 
        
        // 3. Set all hidden thresholds to 0. 
        // (Sum will be 15. Since 15 >= 0, all 16 hidden neurons will fire)
        h_thresholds = 0;           
        
        // 4. Set all output weights to +1
        o_weights = 16'hFFFF;       
        
        // 5. Set output threshold to 10. 
        // (Output sum will be 16. Since 16 >= 10, classification will be 1)
        o_threshold = 16'sd10;        

        // Wait for combinational logic to settle
        #10;
        
        // Verification prints
        $display("--- End to End Test ---");
        $display("Classification: %b | Expected: 1", classification);
        if (classification == 1'b1)
            $display("Result: DDoS Detected (SUCCESS)");
        else
            $display("Result: Benign (FAILED)");

        $finish;
    end
endmodule
