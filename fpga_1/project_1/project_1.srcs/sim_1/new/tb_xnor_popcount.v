`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/14/2026 12:21:25 AM
// Design Name: 
// Module Name: tb_xnor_popcount
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
module tb_xnor_popcount;

    parameter WIDTH = 64;

    reg  [63:0] inputs;
    reg  [63:0] weights;

    wire [63:0] matches;
    wire [6:0]  count;

    integer pass_count;
    integer fail_count;


    // ============================================================
    // DUT
    // ============================================================

    xnor_popcount #(
        .WIDTH(WIDTH)
    ) dut (
        .inputs(inputs),
        .weights(weights),
        .matches(matches),
        .count(count)
    );


    // ============================================================
    // TEST TASK
    // ============================================================

    task check_xnor_popcount;

        input [63:0] test_inputs;
        input [63:0] test_weights;
        input [63:0] expected_matches;
        input [6:0]  expected_count;
        input integer test_number;

        begin

            inputs  = test_inputs;
            weights = test_weights;

            #10;

            if ((matches === expected_matches) &&
                (count === expected_count)) begin

                $display(
                    "TEST %0d: PASS",
                    test_number
                );

                $display(
                    "  INPUT   = %016h",
                    test_inputs
                );

                $display(
                    "  WEIGHT  = %016h",
                    test_weights
                );

                $display(
                    "  XNOR    = %016h",
                    matches
                );

                $display(
                    "  COUNT   = %0d",
                    count
                );

                pass_count = pass_count + 1;

            end
            else begin

                $display(
                    "TEST %0d: FAIL",
                    test_number
                );

                $display(
                    "  INPUT            = %016h",
                    test_inputs
                );

                $display(
                    "  WEIGHT           = %016h",
                    test_weights
                );

                $display(
                    "  EXPECTED XNOR    = %016h",
                    expected_matches
                );

                $display(
                    "  ACTUAL XNOR      = %016h",
                    matches
                );

                $display(
                    "  EXPECTED COUNT   = %0d",
                    expected_count
                );

                $display(
                    "  ACTUAL COUNT     = %0d",
                    count
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

        $display("");
        $display("============================================================");
        $display("XNOR + POPCOUNT TEST");
        $display("64-BIT INPUT + 64-BIT WEIGHT");
        $display("============================================================");


        // TEST 1
        // Everything matches

        check_xnor_popcount(
            64'hFFFFFFFFFFFFFFFF,
            64'hFFFFFFFFFFFFFFFF,
            64'hFFFFFFFFFFFFFFFF,
            7'd64,
            1
        );


        // TEST 2
        // Nothing matches

        check_xnor_popcount(
            64'hFFFFFFFFFFFFFFFF,
            64'h0000000000000000,
            64'h0000000000000000,
            7'd0,
            2
        );


        // TEST 3
        // 32 matches

        check_xnor_popcount(
            64'hAAAAAAAAAAAAAAAA,
            64'hAAAAAAAAAAAAAAAA,
            64'hFFFFFFFFFFFFFFFF,
            7'd64,
            3
        );


        // TEST 4
        // Nothing matches

        check_xnor_popcount(
            64'hAAAAAAAAAAAAAAAA,
            64'h5555555555555555,
            64'h0000000000000000,
            7'd0,
            4
        );


        // TEST 5
        // Known pattern

        check_xnor_popcount(
            64'h123456789ABCDEF0,
            64'hFEDCBA9876543210,
            64'h1317131F1317131F,
            7'd30,
            5
        );


        // TEST 6
        // Random-style pattern

        check_xnor_popcount(
            64'hD50598BC638ADF52,
            64'h038FE6CA9D7826FB,
            64'h29758189010D0656,
            7'd23,
            6
        );


        // TEST 7
        // Another pattern

        check_xnor_popcount(
            64'h5B9232D4365DC077,
            64'h156B16EF0ACC4517,
            64'hB106DBC4C36E7A9F,
            7'd35,
            7
        );


        // TEST 8
        // All zeros

        check_xnor_popcount(
            64'h0000000000000000,
            64'h0000000000000000,
            64'hFFFFFFFFFFFFFFFF,
            7'd64,
            8
        );


        // ========================================================
        // SUMMARY
        // ========================================================

        $display("");
        $display("============================================================");
        $display("XNOR + POPCOUNT VERIFICATION COMPLETE");
        $display("PASS = %0d", pass_count);
        $display("FAIL = %0d", fail_count);
        $display("============================================================");

        if (fail_count == 0)
            $display("XNOR + POPCOUNT TEST PASSED");
        else
            $display("XNOR + POPCOUNT TEST FAILED");

        $display("");

        $finish;

    end

endmodule
