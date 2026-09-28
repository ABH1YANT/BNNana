`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/14/2026 12:37:37 AM
// Design Name: 
// Module Name: tb_threshold_compare
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
module tb_threshold_compare;

    reg [6:0] count;
    reg [6:0] threshold;

    wire output_bit;

    integer pass_count;
    integer fail_count;


    threshold_compare dut (
        .count(count),
        .threshold(threshold),
        .output_bit(output_bit)
    );


    task check_compare;

        input [6:0] test_count;
        input [6:0] test_threshold;
        input        expected;
        input integer test_number;

        begin

            count     = test_count;
            threshold = test_threshold;

            #10;

            if (output_bit === expected) begin

                $display(
                    "TEST %0d: PASS  COUNT=%0d  THRESHOLD=%0d  OUTPUT=%0d",
                    test_number,
                    test_count,
                    test_threshold,
                    output_bit
                );

                pass_count = pass_count + 1;

            end
            else begin

                $display(
                    "TEST %0d: FAIL",
                    test_number
                );

                $display(
                    "  COUNT     = %0d",
                    test_count
                );

                $display(
                    "  THRESHOLD = %0d",
                    test_threshold
                );

                $display(
                    "  EXPECTED  = %0d",
                    expected
                );

                $display(
                    "  ACTUAL    = %0d",
                    output_bit
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
        $display("THRESHOLD COMPARE TEST");
        $display("7-BIT COUNT -> 1-BIT OUTPUT");
        $display("============================================================");


        // TEST 1
        // Count below threshold

        check_compare(
            7'd20,
            7'd28,
            1'b0,
            1
        );


        // TEST 2
        // Count above threshold

        check_compare(
            7'd35,
            7'd28,
            1'b1,
            2
        );


        // TEST 3
        // Exactly equal
        // Must be 0 because comparison is >

        check_compare(
            7'd28,
            7'd28,
            1'b0,
            3
        );


        // TEST 4
        // Minimum possible count

        check_compare(
            7'd0,
            7'd0,
            1'b0,
            4
        );


        // TEST 5
        // One above zero

        check_compare(
            7'd1,
            7'd0,
            1'b1,
            5
        );


        // TEST 6
        // Maximum count, threshold 63

        check_compare(
            7'd64,
            7'd63,
            1'b1,
            6
        );


        // TEST 7
        // Maximum count equals maximum threshold

        check_compare(
            7'd64,
            7'd64,
            1'b0,
            7
        );


        // TEST 8
        // Actual Layer 1 neuron 0 threshold
        // 001C hex = 28

        check_compare(
            7'd29,
            7'd28,
            1'b1,
            8
        );


        // TEST 9
        // Actual Layer 1 neuron 17 threshold
        // 0040 hex = 64

        check_compare(
            7'd63,
            7'd64,
            1'b0,
            9
        );


        // TEST 10
        // Actual Layer 1 neuron 50 threshold
        // 0000 hex = 0

        check_compare(
            7'd1,
            7'd0,
            1'b1,
            10
        );


        // ========================================================
        // SUMMARY
        // ========================================================

        $display("");
        $display("============================================================");
        $display("THRESHOLD COMPARE VERIFICATION COMPLETE");
        $display("PASS = %0d", pass_count);
        $display("FAIL = %0d", fail_count);
        $display("============================================================");

        if (fail_count == 0)
            $display("THRESHOLD COMPARE TEST PASSED");
        else
            $display("THRESHOLD COMPARE TEST FAILED");

        $display("");

        $finish;

    end

endmodule
