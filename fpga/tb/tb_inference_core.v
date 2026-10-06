`timescale 1ns / 1ps

module tb_inference_core;

    reg         clk;
    reg         rst;
    reg         start;
    reg [127:0] features;

    wire        classification;
    wire        inference_done;
    wire        busy;

    integer pass_count;
    integer fail_count;
    integer i;

    // ============================================================
    // DUT
    // ============================================================

    inference_core dut (
        .clk(clk),
        .rst(rst),
        .start(start),
        .features(features),
        .classification(classification),
        .inference_done(inference_done),
        .busy(busy)
    );

    // ============================================================
    // Clock: 100 MHz
    // ============================================================

    initial begin
        clk = 1'b0;

        forever #5 clk = ~clk;
    end

    // ============================================================
    // Run one test
    // ============================================================

    task run_test;
        input [127:0] test_features;
        input          expected;
        begin

            // Present input
            @(negedge clk);
            features = test_features;

            // Start inference
            start = 1'b1;

            @(negedge clk);
            start = 1'b0;

            // Wait for completion
            wait(inference_done == 1'b1);

            #1;

            if (classification === expected) begin
                $display(
                    "PASS: input=%032h expected=%0d got=%0d",
                    test_features,
                    expected,
                    classification
                );

                pass_count = pass_count + 1;
            end
            else begin
                $display(
                    "FAIL: input=%032h expected=%0d got=%0d",
                    test_features,
                    expected,
                    classification
                );

                fail_count = fail_count + 1;
            end

            // Give one cycle before next test
            @(negedge clk);
        end
    endtask

    // ============================================================
    // Test sequence
    // ============================================================

    initial begin

        pass_count = 0;
        fail_count = 0;

        rst      = 1'b1;
        start    = 1'b0;
        features = 128'd0;

        repeat(3) @(negedge clk);

        rst = 1'b0;

        // ========================================================
        // Same 10 functional vectors used for the previous
        // verified pipelined inference_core.
        // ========================================================

        run_test(
            128'h00000000000000000000000000000000,
            1'b0
        );

        run_test(
            128'hFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            1'b0
        );

        run_test(
            128'hAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA,
            1'b0
        );

        run_test(
            128'h55555555555555555555555555555555,
            1'b0
        );

        run_test(
            128'h0123456789ABCDEF0123456789ABCDEF,
            1'b0
        );

        run_test(
            128'hFEDCBA9876543210FEDCBA9876543210,
            1'b1
        );

        run_test(
            128'h0123456789ABCDEF00123456789ABCDE,
            1'b0
        );

        run_test(
            128'h80000000000000008000000000000000,
            1'b1
        );

        run_test(
            128'h7FFFFFFFFFFFFFFF7FFFFFFFFFFFFFFF,
            1'b0
        );

        run_test(
            128'h13579BDF2468ACE013579BDF2468ACE0,
            1'b0
        );

        // ========================================================
        // Final result
        // ========================================================

        $display("");
        $display("==============================================");
        $display("INFERENCE CORE PIPELINE TEST RESULT");
        $display("==============================================");

        $display("PASS = %0d", pass_count);
        $display("FAIL = %0d", fail_count);

        if (fail_count == 0)
            $display("NEW PIPELINED INFERENCE CORE TEST PASSED");
        else
            $display("NEW PIPELINED INFERENCE CORE TEST FAILED");

        $display("==============================================");

        #100;
        $finish;

    end

endmodule