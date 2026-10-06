`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/27/2026 12:47:43 PM
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
`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// BNNana
// Output Layer Testbench
//
// 160 binary inputs -> 1 binary output
//
// Weight:
//     F3E67C70AD428AFAB34FCC616F3069A5399D4F3F
//
// Threshold:
//     81
//////////////////////////////////////////////////////////////////////////////////

module tb_output_layer;

    reg  [159:0] inputs;
    wire         output_bit;

    integer pass_count;
    integer fail_count;


    // ============================================================
    // DUT
    // ============================================================

    output_layer dut (
        .inputs(inputs),
        .output_bit(output_bit)
    );


    // ============================================================
    // TEST TASK
    // ============================================================

    task run_test;

        input [159:0] test_input;
        input         expected_output;
        input integer test_number;

        begin

            inputs = test_input;

            #1;

            if (output_bit === expected_output) begin

                $display(
                    "TEST %0d: PASS  INPUT=%040h  OUTPUT=%b",
                    test_number,
                    inputs,
                    output_bit
                );

                pass_count = pass_count + 1;

            end

            else begin

                $display(
                    "TEST %0d: FAIL  INPUT=%040h  EXPECTED=%b  ACTUAL=%b",
                    test_number,
                    inputs,
                    expected_output,
                    output_bit
                );

                fail_count = fail_count + 1;

            end

        end

    endtask


    // ============================================================
    // TESTS
    // ============================================================

    initial begin

        pass_count = 0;
        fail_count = 0;

        inputs = 160'd0;

        #10;

        $display("");
        $display("============================================================");
        $display("OUTPUT LAYER TEST");
        $display("160 INPUTS -> 1 BINARY OUTPUT");
        $display("============================================================");


        // --------------------------------------------------------
        // TEST 1
        // Popcount = 72
        // 72 > 81 = 0
        // --------------------------------------------------------

        run_test(
            160'h0000000000000000000000000000000000000000,
            1'b0,
            1
        );


        // --------------------------------------------------------
        // TEST 2
        // Popcount = 88
        // 88 > 81 = 1
        // --------------------------------------------------------

        run_test(
            160'hFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            1'b1,
            2
        );


        // --------------------------------------------------------
        // TEST 3
        // Popcount = 82
        // 82 > 81 = 1
        // --------------------------------------------------------

        run_test(
            160'hAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA,
            1'b1,
            3
        );


        // --------------------------------------------------------
        // TEST 4
        // Popcount = 78
        // 78 > 81 = 0
        // --------------------------------------------------------

        run_test(
            160'h5555555555555555555555555555555555555555,
            1'b0,
            4
        );


        // --------------------------------------------------------
        // TEST 5
        // Popcount = 81
        // 81 > 81 = 0
        // --------------------------------------------------------

        run_test(
            160'h123456789ABCDEF0123456789ABCDEF012345678,
            1'b0,
            5
        );


        // --------------------------------------------------------
        // TEST 6
        // Popcount = 87
        // 87 > 81 = 1
        // --------------------------------------------------------

        run_test(
            160'hD50598BC638ADF52947BCC8F3697082F3A86C29C,
            1'b1,
            6
        );


        // --------------------------------------------------------
        // TEST 7
        // Popcount = 84
        // 84 > 81 = 1
        // --------------------------------------------------------

        run_test(
            160'h5B9232D4365DC077947BCC8F3697082FC8BCB671,
            1'b1,
            7
        );


        // --------------------------------------------------------
        // TEST 8
        // Popcount = 73
        // 73 > 81 = 0
        // --------------------------------------------------------

        run_test(
            160'h0000000000000000000000000000000000000001,
            1'b0,
            8
        );


        // --------------------------------------------------------
        // TEST 9
        // Popcount = 84
        // 84 > 81 = 1
        // --------------------------------------------------------

        run_test(
            160'hFEDCBA98765432100123456789ABCDEF3A86C29C,
            1'b1,
            9
        );


        // --------------------------------------------------------
        // TEST 10
        // Popcount = 76
        // 76 > 81 = 0
        // --------------------------------------------------------

        run_test(
            160'h947BCC8F3697082F3A86C29C07D0909868BD5453,
            1'b0,
            10
        );


        // ========================================================
        // FINAL RESULT
        // ========================================================

        $display("");
        $display("============================================================");
        $display("OUTPUT LAYER VERIFICATION COMPLETE");
        $display("PASS = %0d", pass_count);
        $display("FAIL = %0d", fail_count);
        $display("============================================================");

        if (fail_count == 0)
            $display("OUTPUT LAYER TEST PASSED");
        else
            $display("OUTPUT LAYER TEST FAILED");

        $display("");

        #10;

        $finish;

    end

endmodule
