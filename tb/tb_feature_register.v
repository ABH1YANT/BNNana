`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/26/2026 01:36:09 AM
// Design Name: 
// Module Name: tb_feature_register
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


module tb_feature_register();

    parameter FEATURE_COUNT = 15;
    parameter FEATURE_WIDTH = 8;
    parameter CLK_PERIOD = 10;

    reg clk;
    reg rst;
    reg [(FEATURE_COUNT * FEATURE_WIDTH)-1:0] feature_vector;
    reg load_enable;
    
    wire [(FEATURE_COUNT * FEATURE_WIDTH)-1:0] registered_features;

    // Instantiate the Unit Under Test (UUT)
    feature_register #(
        .FEATURE_COUNT(FEATURE_COUNT),
        .FEATURE_WIDTH(FEATURE_WIDTH)
    ) uut (
        .clk(clk),
        .rst(rst),
        .feature_vector(feature_vector),
        .load_enable(load_enable),
        .registered_features(registered_features)
    );

    // Generate 100 MHz Clock
    always #(CLK_PERIOD/2) clk = ~clk;

    initial begin
        // Initialize Inputs
        clk = 0;
        rst = 1;
        feature_vector = 0;
        load_enable = 0;

        #100;
        rst = 0;
        #100;

        $display("--- Starting Feature Register Simulation ---");

        // ---------------------------------------------------------
        // Test 1: Data present, but no enable pulse
        // ---------------------------------------------------------
        // We put 0xAA on all 15 bytes
        feature_vector = {FEATURE_COUNT{8'hAA}}; 
        #30; // Wait a few clock cycles
        $display("Test 1 (No Enable): Output = 0x%h | Expected = 0x0", registered_features);

        // ---------------------------------------------------------
        // Test 2: Pulse load_enable
        // ---------------------------------------------------------
        load_enable = 1'b1;
        #CLK_PERIOD; // Pulse for exactly 1 clock cycle
        load_enable = 1'b0;
        #30;
        $display("Test 2 (Load Data): Output = 0x%h | Expected = 0x%h", registered_features, {FEATURE_COUNT{8'hAA}});

        // ---------------------------------------------------------
        // Test 3: Change input, ensure output holds steady
        // ---------------------------------------------------------
        // The packet parser starts receiving a new packet (0xBB)
        feature_vector = {FEATURE_COUNT{8'hBB}}; 
        #30;
        $display("Test 3 (Hold Data): Output = 0x%h | Expected = 0x%h", registered_features, {FEATURE_COUNT{8'hAA}});

        // ---------------------------------------------------------
        // Test 4: Reset
        // ---------------------------------------------------------
        rst = 1'b1;
        #30;
        rst = 1'b0;
        $display("Test 4 (Reset)    : Output = 0x%h | Expected = 0x0", registered_features);

        #50;
        $display("--- Simulation Complete ---");
        $finish;
    end

endmodule
