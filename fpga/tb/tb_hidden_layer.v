`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/14/2026 12:46:27 AM
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
module tb_hidden_layer;

    reg  [63:0] inputs;
    wire [63:0] outputs;

    integer pass_count;
    integer fail_count;


    hidden_layer dut (
        .inputs(inputs),
        .outputs(outputs)
    );


    task check_layer;

        input [63:0] test_input;
        input [63:0] expected;
        input integer test_number;

        begin

            inputs = test_input;

            #10;

            if (outputs === expected) begin

                $display(
                    "TEST %0d: PASS  INPUT=%016h  OUTPUT=%016h",
                    test_number,
                    test_input,
                    outputs
                );

                pass_count = pass_count + 1;

            end
            else begin

                $display(
                    "TEST %0d: FAIL",
                    test_number
                );

                $display(
                    "  INPUT    = %016h",
                    test_input
                );

                $display(
                    "  EXPECTED = %016h",
                    expected
                );

                $display(
                    "  ACTUAL   = %016h",
                    outputs
                );

                fail_count = fail_count + 1;

            end

        end

    endtask


    initial begin

        pass_count = 0;
        fail_count = 0;

        $display("");
        $display("============================================================");
        $display("LAYER 1 TEST");
        $display("64 INPUTS -> 64 BINARY OUTPUTS");
        $display("============================================================");


        // TEST 1: All zeros

        check_layer(
            64'h0000000000000000,
            64'h3B86919C05D19999,
            1
        );


        // TEST 2: All ones

        check_layer(
            64'hFFFFFFFFFFFFFFFF,
            64'hEA9688BC045491DD,
            2
        );


        // TEST 3: Alternating pattern

        check_layer(
            64'hAAAAAAAAAAAAAAAA,
            64'h6A9688D805D190D5,
            3
        );


        // TEST 4: Opposite alternating pattern

        check_layer(
            64'h5555555555555555,
            64'hE2A4939C20549DD8,
            4
        );


        // TEST 5: Known binary pattern

        check_layer(
            64'h123456789ABCDEF0,
            64'hEA960ADC045591DD,
            5
        );


        // TEST 6: Random-style pattern

        check_layer(
            64'hD50598BC638ADF52,
            64'h6AA45B9C2150919C,
            6
        );


        // TEST 7: Random-style pattern

        check_layer(
            64'h5B9232D4365DC077,
            64'hEAB6099C0454919D,
            7
        );


        // TEST 8: Single bit

        check_layer(
            64'h0000000000000001,
            64'h3B86019805D19999,
            8
        );


        // TEST 9: Complementary pattern

        check_layer(
            64'hFEDCBA9876543210,
            64'hEE960B98245491D9,
            9
        );


        // TEST 10: Layer 0-style output

        check_layer(
            64'h947BCC8F3697082F,
            64'h3A86C29C07D09098,
            10
        );


        // ========================================================
        // SUMMARY
        // ========================================================

        $display("");
        $display("============================================================");
        $display("LAYER 1 VERIFICATION COMPLETE");
        $display("PASS = %0d", pass_count);
        $display("FAIL = %0d", fail_count);
        $display("============================================================");

        if (fail_count == 0)
            $display("LAYER 1 TEST PASSED");
        else
            $display("LAYER 1 TEST FAILED");

        $display("");

        $finish;

    end

endmodule
