`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/22/2026 10:45:57 PM
// Design Name: 
// Module Name: tb_accumulator
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


module tb_accumulator();

    // We override the parameters to 3 inputs just for easy manual math verification
    parameter INPUT_COUNT = 3;
    parameter INPUT_WIDTH = 8;
    parameter ACC_WIDTH = 16;

    // Inputs to the module (Registers in testbench)
    reg [(INPUT_COUNT * INPUT_WIDTH)-1:0] feature_values;
    reg [INPUT_COUNT-1:0] weight_bits;

    // Outputs from the module (Wires in testbench)
    wire signed [ACC_WIDTH-1:0] accumulated_sum;

    // Instantiate the Unit Under Test (UUT)
    accumulator #(
        .INPUT_COUNT(INPUT_COUNT),
        .INPUT_WIDTH(INPUT_WIDTH),
        .ACC_WIDTH(ACC_WIDTH)
    ) uut (
        .feature_values(feature_values),
        .weight_bits(weight_bits),
        .accumulated_sum(accumulated_sum)
    );

    initial begin
        // Initialize Inputs
        feature_values = 0;
        weight_bits = 0;

        // Wait 100 ns for global reset to finish
        #100;
        
        // Load features: Feature 2 = 30, Feature 1 = 20, Feature 0 = 10
        // We concatenate them into a single flat vector
        feature_values = {8'd30, 8'd20, 8'd10};

        // ---------------------------------------------------------
        // Test Case 1: All +1
        // w[2]=1, w[1]=1, w[0]=1 => (+30) + (+20) + (+10) = 60
        // ---------------------------------------------------------
        weight_bits = 3'b111;
        #10; // Wait 10ns for combinational logic to settle
        $display("Test 1 (All +1): Weights=%b, Sum=%d | Expected: 60", weight_bits, accumulated_sum);

        // ---------------------------------------------------------
        // Test Case 2: Mixed Weights
        // w[2]=0, w[1]=1, w[0]=1 => (-30) + (+20) + (+10) = 0
        // ---------------------------------------------------------
        weight_bits = 3'b011;
        #10;
        $display("Test 2 (Mixed) : Weights=%b, Sum=%d | Expected: 0", weight_bits, accumulated_sum);

        // ---------------------------------------------------------
        // Test Case 3: All -1 (Testing Negative Numbers)
        // w[2]=0, w[1]=0, w[0]=0 => (-30) + (-20) + (-10) = -60
        // ---------------------------------------------------------
        weight_bits = 3'b000;
        #10;
        $display("Test 3 (All -1): Weights=%b, Sum=%d | Expected: -60", weight_bits, accumulated_sum);

        // End simulation
        #10;
        $finish;
    end

endmodule
