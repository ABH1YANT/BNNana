`timescale 1ns / 1ps

module tb_accumulator;

    localparam INPUT_COUNT = 16;
    localparam INPUT_WIDTH = 8;
    localparam ACC_WIDTH   = 16;

    reg [127:0] inputs;
    reg [15:0]  weights;

    wire signed [15:0] sum;

    integer pass_count;
    integer fail_count;

    accumulator #(
        .INPUT_COUNT(INPUT_COUNT),
        .INPUT_WIDTH(INPUT_WIDTH),
        .ACC_WIDTH(ACC_WIDTH)
    ) dut (
        .inputs(inputs),
        .weights(weights),
        .sum(sum)
    );

    // ============================================================
    // Test task
    // ============================================================

    task run_test;
        input [127:0] test_inputs;
        input [15:0]  test_weights;
        input integer expected;

        begin

            inputs  = test_inputs;
            weights = test_weights;

            #10;

            if (sum === expected) begin

                $display(
                    "PASS: inputs=%032h weights=%04h expected=%0d got=%0d",
                    test_inputs,
                    test_weights,
                    expected,
                    sum
                );

                pass_count = pass_count + 1;

            end
            else begin

                $display(
                    "FAIL: inputs=%032h weights=%04h expected=%0d got=%0d",
                    test_inputs,
                    test_weights,
                    expected,
                    sum
                );

                fail_count = fail_count + 1;

            end
        end
    endtask


    // ============================================================
    // Tests
    // ============================================================

    initial begin

        pass_count = 0;
        fail_count = 0;

        inputs  = 128'd0;
        weights = 16'd0;

        #10;

        // --------------------------------------------------------
        // Test 1
        // All inputs = 1
        // All weights = +1
        // Result = 16
        // --------------------------------------------------------

        run_test(
            128'h01010101010101010101010101010101,
            16'hFFFF,
            16
        );

        // --------------------------------------------------------
        // Test 2
        // All inputs = 1
        // All weights = -1
        // Result = -16
        // --------------------------------------------------------

        run_test(
            128'h01010101010101010101010101010101,
            16'h0000,
            -16
        );

        // --------------------------------------------------------
        // Test 3
        // Inputs = 1..16
        // All +1
        // Sum = 136
        // --------------------------------------------------------

        run_test(
            128'h100F0E0D0C0B0A090807060504030201,
            16'hFFFF,
            136
        );

        // --------------------------------------------------------
        // Test 4
        // Inputs = 1..16
        // All -1
        // Sum = -136
        // --------------------------------------------------------

        run_test(
            128'h100F0E0D0C0B0A090807060504030201,
            16'h0000,
            -136
        );

        // --------------------------------------------------------
        // Test 5
        // Alternating +1/-1
        // Expected = -80
        // --------------------------------------------------------

        run_test(
            128'hA0A09696827D6E64503C32281E140A0A,
            16'hAAAA,
            55
        );

        // --------------------------------------------------------
        // Test 6
        // Maximum input, all +1
        // 16 * 255 = 4080
        // --------------------------------------------------------

        run_test(
            128'hFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            16'hFFFF,
            4080
        );

        // --------------------------------------------------------
        // Test 7
        // Maximum input, all -1
        // -16 * 255 = -4080
        // --------------------------------------------------------

        run_test(
            128'hFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            16'h0000,
            -4080
        );

        // --------------------------------------------------------
        // Test 8
        // Mixed weights
        // Expected = -16
        // --------------------------------------------------------

        run_test(
            128'h100F0E0D0C0B0A090807060504030201,
            16'h33CC,
            0
        );

        // ========================================================
        // Final result
        // ========================================================

        $display("");
        $display("==============================================");
        $display("BALANCED ACCUMULATOR TEST RESULT");
        $display("==============================================");

        $display("PASS = %0d", pass_count);
        $display("FAIL = %0d", fail_count);

        if (fail_count == 0)
            $display("BALANCED ACCUMULATOR TEST PASSED");
        else
            $display("BALANCED ACCUMULATOR TEST FAILED");

        $display("==============================================");

        #20;
        $finish;

    end

endmodule