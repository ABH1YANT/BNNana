`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/27/2026 04:57:58 PM
// Design Name: 
// Module Name: tb_controller_fsm
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

module tb_controller_fsm;

    reg clk;
    reg rst;

    reg start;
    reg inference_done;

    wire inference_start;
    wire busy;
    wire result_valid;

    integer pass_count;
    integer fail_count;

    // ------------------------------------------------------------
    // DUT
    // ------------------------------------------------------------

    controller_fsm dut (
        .clk(clk),
        .rst(rst),

        .start(start),
        .inference_done(inference_done),

        .inference_start(inference_start),
        .busy(busy),
        .result_valid(result_valid)
    );

    // ------------------------------------------------------------
    // Clock
    // 10 ns period
    // ------------------------------------------------------------

    always #5 clk = ~clk;

    // ------------------------------------------------------------
    // Check task
    // ------------------------------------------------------------

    task check_outputs;
        input expected_start;
        input expected_busy;
        input expected_valid;
        input integer test_number;

        begin

            #1;

            if ((inference_start === expected_start) &&
                (busy            === expected_busy) &&
                (result_valid    === expected_valid)) begin

                $display(
                    "TEST %0d: PASS start=%b busy=%b valid=%b",
                    test_number,
                    inference_start,
                    busy,
                    result_valid
                );

                pass_count = pass_count + 1;

            end
            else begin

                $display(
                    "TEST %0d: FAIL start=%b busy=%b valid=%b | EXPECTED start=%b busy=%b valid=%b",
                    test_number,
                    inference_start,
                    busy,
                    result_valid,
                    expected_start,
                    expected_busy,
                    expected_valid
                );

                fail_count = fail_count + 1;

            end
        end
    endtask

    // ------------------------------------------------------------
    // Test sequence
    // ------------------------------------------------------------

    initial begin

        clk = 1'b0;
        rst = 1'b1;

        start = 1'b0;
        inference_done = 1'b0;

        pass_count = 0;
        fail_count = 0;

        $display("");
        $display("==============================================");
        $display(" CONTROLLER FSM TEST");
        $display("==============================================");

        // --------------------------------------------------------
        // Reset
        // --------------------------------------------------------

        @(posedge clk);
        #1;

        check_outputs(
            1'b0,
            1'b0,
            1'b0,
            1
        );

        rst = 1'b0;

        // --------------------------------------------------------
        // IDLE
        // --------------------------------------------------------

        @(posedge clk);

        check_outputs(
            1'b0,
            1'b0,
            1'b0,
            2
        );

        // --------------------------------------------------------
        // Start inference
        // --------------------------------------------------------

        start = 1'b1;

        @(posedge clk);

        check_outputs(
            1'b1,
            1'b1,
            1'b0,
            3
        );

        // --------------------------------------------------------
        // Keep start asserted
        // Controller remains RUN
        // --------------------------------------------------------

        @(posedge clk);

        check_outputs(
            1'b1,
            1'b1,
            1'b0,
            4
        );

        // --------------------------------------------------------
        // Inference completes
        // --------------------------------------------------------

        inference_done = 1'b1;

        @(posedge clk);

        check_outputs(
            1'b0,
            0,
            1'b1,
            5
        );

        // --------------------------------------------------------
        // Clear inputs
        // --------------------------------------------------------

        inference_done = 1'b0;
        start = 1'b0;

        @(posedge clk);

        check_outputs(
            1'b0,
            1'b0,
            1'b0,
            6
        );

        // --------------------------------------------------------
        // Start second inference
        // --------------------------------------------------------

        start = 1'b1;

        @(posedge clk);

        check_outputs(
            1'b1,
            1'b1,
            1'b0,
            7
        );

        // --------------------------------------------------------
        // Complete second inference
        // --------------------------------------------------------

        inference_done = 1'b1;

        @(posedge clk);

        check_outputs(
            1'b0,
            1'b0,
            1'b1,
            8
        );

        // --------------------------------------------------------
        // Return to IDLE
        // --------------------------------------------------------

        inference_done = 1'b0;
        start = 1'b0;

        @(posedge clk);

        check_outputs(
            1'b0,
            1'b0,
            1'b0,
            9
        );

        // --------------------------------------------------------
        // Summary
        // --------------------------------------------------------

        $display("");
        $display("==============================================");
        $display("PASS = %0d", pass_count);
        $display("FAIL = %0d", fail_count);
        $display("==============================================");

        if (fail_count == 0)
            $display("CONTROLLER FSM TEST PASSED");
        else
            $display("CONTROLLER FSM TEST FAILED");

        $display("");

        #10;
        $finish;

    end

endmodule