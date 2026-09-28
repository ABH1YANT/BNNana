`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/27/2026 04:24:51 PM
// Design Name: 
// Module Name: tb_inference_core_debug
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

module tb_inference_core_debug;

    reg  [127:0] features;
    wire         classification;

    // ------------------------------------------------------------
    // Internal signals exposed from the DUT
    // through hierarchical references.
    // ------------------------------------------------------------

    wire [63:0] layer0_out;
    wire [63:0] layer1_out;
    wire [31:0] layer2_out;

    assign layer0_out = dut.layer0_output;
    assign layer1_out = dut.layer1_output;
    assign layer2_out = dut.layer2_output;

    // ------------------------------------------------------------
    // DUT
    // ------------------------------------------------------------

    inference_core dut (
        .features(features),
        .classification(classification)
    );

    // ------------------------------------------------------------
    // Test task
    // ------------------------------------------------------------

    task run_test;
        input [127:0] test_features;
        input integer test_number;

        begin

            features = test_features;

            // Allow entire combinational chain to settle
            #10;

            $display("");
            $display("----------------------------------------------");
            $display("TEST %0d", test_number);
            $display("----------------------------------------------");

            $display("INPUT  = %032h", features);
            $display("LAYER0 = %016h", layer0_out);
            $display("LAYER1 = %016h", layer1_out);
            $display("LAYER2 = %08h",  layer2_out);
            $display("FINAL  = %b",     classification);

        end
    endtask

    // ------------------------------------------------------------
    // Tests
    // ------------------------------------------------------------

    initial begin

        features = 128'd0;

        $display("");
        $display("==============================================");
        $display(" INFERENCE CORE DEBUG TEST");
        $display(" ==============================================");
        $display(" FEATURES -> L0 -> L1 -> L2 -> OUTPUT");
        $display("==============================================");

        // Test 1
        run_test(
            128'h00000000000000000000000000000000,
            1
        );

        // Test 2
        run_test(
            128'hFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            2
        );

        // Test 3
        run_test(
            128'h01010101010101010101010101010101,
            3
        );

        // Test 4
        run_test(
            128'h0F0E0D0C0B0A09080706050403020100,
            4
        );

        // Test 5
        run_test(
            128'hFFF2E5D8CBBEB1A4978A7D706356493C,
            5
        );

        // Test 6
        run_test(
            128'hD50598BC638ADF52947BCC8F3697082E,
            6
        );

        // Test 7
        run_test(
            128'hD3550353B75B0D8F5B9232D4365DC077,
            7
        );

        // Test 8
        run_test(
            128'h5B9232D4365DC077947BCC8F3697082F,
            8
        );

        // Test 9
        run_test(
            128'hDE42A9B6C3D0E7F4191F2C3D4E5F6071,
            9
        );

        // Test 10
        run_test(
            128'hE32817F6D5C4B3A291807766554467BA,
            10
        );

        $display("");
        $display("==============================================");
        $display(" DEBUG TEST COMPLETE");
        $display("==============================================");

        #10;
        $finish;

    end

endmodule