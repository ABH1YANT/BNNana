`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/13/2026 11:00:00 PM
// Design Name: 
// Module Name: tb_bnn_neuron
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
module tb_bnn_neuron;

    parameter INPUT_COUNT = 16;
    parameter INPUT_WIDTH = 8;
    parameter ACC_WIDTH   = 16;

    reg [127:0] inputs;
    reg [15:0] weights;

    reg signed [15:0] threshold;

    wire output_bit;

    integer expected;


    // ============================================================
    // DUT
    // ============================================================

    bnn_neuron dut (

        .inputs(inputs),
        .weights(weights),
        .threshold(threshold),
        .output_bit(output_bit)

    );


    // ============================================================
    // TEST
    // ============================================================

    initial begin

        $display("");
        $display("============================================");
        $display("BNN NEURON TEST - 16 BIT");
        $display("============================================");


        // ========================================================
        // TEST 1
        // Sum = 0
        // Threshold = 10
        // Expected = 0
        // ========================================================

        inputs = 128'h0;
        weights = 16'hFFFF;
        threshold = 16'sd10;

        #10;

        expected = 0;

        if (output_bit == expected)
            $display("TEST 1: PASS");
        else
            $display(
                "TEST 1: FAIL expected=%0d actual=%0d",
                expected,
                output_bit
            );


        // ========================================================
        // TEST 2
        // Sum = 16
        // Threshold = 10
        // Expected = 1
        // ========================================================

        inputs = 128'h01010101010101010101010101010101;
        weights = 16'hFFFF;
        threshold = 16'sd10;

        #10;

        expected = 1;

        if (output_bit == expected)
            $display("TEST 2: PASS");
        else
            $display(
                "TEST 2: FAIL expected=%0d actual=%0d",
                expected,
                output_bit
            );


        // ========================================================
        // TEST 3
        // Sum = 16
        // Threshold = 16
        // Expected = 0
        // ========================================================

        inputs = 128'h01010101010101010101010101010101;
        weights = 16'hFFFF;
        threshold = 16'sd16;

        #10;

        expected = 0;

        if (output_bit == expected)
            $display("TEST 3: PASS");
        else
            $display(
                "TEST 3: FAIL expected=%0d actual=%0d",
                expected,
                output_bit
            );


        // ========================================================
        // TEST 4
        // Sum = -160
        // Threshold = -200
        // Expected = 1
        // ========================================================

        inputs = 128'h0A0A0A0A0A0A0A0A0A0A0A0A0A0A0A0A;
        weights = 16'h0000;
        threshold = -16'sd200;

        #10;

        expected = 1;

        if (output_bit == expected)
            $display("TEST 4: PASS");
        else
            $display(
                "TEST 4: FAIL expected=%0d actual=%0d",
                expected,
                output_bit
            );


        // ========================================================
        // TEST 5
        // Sum = -160
        // Threshold = -100
        // Expected = 0
        // ========================================================

        inputs = 128'h0A0A0A0A0A0A0A0A0A0A0A0A0A0A0A0A;
        weights = 16'h0000;
        threshold = -16'sd100;

        #10;

        expected = 0;

        if (output_bit == expected)
            $display("TEST 5: PASS");
        else
            $display(
                "TEST 5: FAIL expected=%0d actual=%0d",
                expected,
                output_bit
            );


        // ========================================================
        // TEST 6
        // Sum = -64
        // Threshold = -100
        // Expected = 1
        // ========================================================

        inputs = 128'h100F0E0D0C0B0A09080706050403020100;
        weights = 16'h00FF;
        threshold = -16'sd100;

        #10;

        expected = 1;

        if (output_bit == expected)
            $display("TEST 6: PASS");
        else
            $display(
                "TEST 6: FAIL expected=%0d actual=%0d",
                expected,
                output_bit
            );


        // ========================================================
        // TEST 7
        // Sum = -64
        // Threshold = -64
        // Expected = 0
        // ========================================================

        inputs = 128'h100F0E0D0C0B0A09080706050403020100;
        weights = 16'h00FF;
        threshold = -16'sd64;

        #10;

        expected = 0;

        if (output_bit == expected)
            $display("TEST 7: PASS");
        else
            $display(
                "TEST 7: FAIL expected=%0d actual=%0d",
                expected,
                output_bit
            );


        // ========================================================
        // TEST 8
        // Maximum positive
        // Sum = 4080
        // Threshold = 4000
        // Expected = 1
        // ========================================================

        inputs = 128'hFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;
        weights = 16'hFFFF;
        threshold = 16'sd4000;

        #10;

        expected = 1;

        if (output_bit == expected)
            $display("TEST 8: PASS");
        else
            $display(
                "TEST 8: FAIL expected=%0d actual=%0d",
                expected,
                output_bit
            );


        // ========================================================
        // TEST 9
        // Maximum negative
        // Sum = -4080
        // Threshold = -4000
        // Expected = 0
        // ========================================================

        inputs = 128'hFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;
        weights = 16'h0000;
        threshold = -16'sd4000;

        #10;

        expected = 0;

        if (output_bit == expected)
            $display("TEST 9: PASS");
        else
            $display(
                "TEST 9: FAIL expected=%0d actual=%0d",
                expected,
                output_bit
            );


        // ========================================================
        // TEST 10
        //
        // Important: large 16-bit threshold
        //
        // Threshold = 10656 = 16'h29A0
        //
        // Sum can never reach it because maximum sum is 4080.
        //
        // Expected = 0
        // ========================================================

        inputs = 128'hFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;
        weights = 16'hFFFF;
        threshold = 16'sh29A0;

        #10;

        expected = 0;

        if (output_bit == expected)
            $display("TEST 10: PASS");
        else
            $display(
                "TEST 10: FAIL expected=%0d actual=%0d",
                expected,
                output_bit
            );


        // ========================================================
        // COMPLETE
        // ========================================================

        $display("");
        $display("============================================");
        $display("BNN NEURON 16-BIT TEST COMPLETE");
        $display("============================================");

        $finish;

    end

endmodule