`timescale 1ns / 1ps

module tb_uart_controller;

    reg clk;
    reg rst;

    reg        result_valid;
    reg        classification;

    wire [7:0] tx_data;
    wire       tx_start;
    reg        tx_busy;
    reg        tx_done;

    wire       busy;

    integer pass_count;
    integer fail_count;

    uart_controller uut (
        .clk(clk),
        .rst(rst),

        .result_valid(result_valid),
        .classification(classification),

        .tx_data(tx_data),
        .tx_start(tx_start),
        .tx_busy(tx_busy),
        .tx_done(tx_done),

        .busy(busy)
    );

    // 10 ns clock
    always #5 clk = ~clk;


    // ============================================================
    // CHECK TASK
    // ============================================================

    task check;
        input condition;
        input [255:0] message;

        begin
            if (condition) begin
                $display("%s: PASS", message);
                pass_count = pass_count + 1;
            end
            else begin
                $display("%s: FAIL", message);
                fail_count = fail_count + 1;
            end
        end
    endtask


    // ============================================================
    // TEST ONE RESULT
    // ============================================================

    task test_result;

        input classification_value;
        input [7:0] expected_data;

        begin

            $display("");
            $display("----------------------------------------------");
            $display("TEST CLASSIFICATION = %d", classification_value);
            $display("----------------------------------------------");

            tx_busy = 1'b0;
            tx_done = 1'b0;


            // ----------------------------------------------------
            // Present inference result
            // ----------------------------------------------------

            @(negedge clk);

            classification = classification_value;
            result_valid = 1'b1;

            @(negedge clk);

            result_valid = 1'b0;


            // ----------------------------------------------------
            // Controller captures result.
            //
            // IMPORTANT:
            // tx_start is generated on THIS SAME clock edge
            // after the controller enters S_SEND.
            // ----------------------------------------------------

            @(posedge clk);
            #1;

            check(
                busy === 1'b1,
                "Controller BUSY after result"
            );

            check(
                tx_data === expected_data,
                "TX DATA correct"
            );

            check(
                tx_start === 1'b1,
                "TX START asserted"
            );


            // ----------------------------------------------------
            // UART accepts the request
            // ----------------------------------------------------

            @(negedge clk);

            tx_busy = 1'b1;


            // On this clock controller enters WAIT and
            // removes the tx_start pulse.
            @(posedge clk);
            #1;

            check(
                tx_start === 1'b0,
                "TX START deasserted"
            );

            check(
                busy === 1'b1,
                "Controller remains BUSY during TX"
            );


            // ----------------------------------------------------
            // UART finishes transmission
            // ----------------------------------------------------

            @(negedge clk);

            tx_busy = 1'b0;
            tx_done = 1'b1;

            @(posedge clk);
            #1;

            check(
                busy === 1'b0,
                "Controller BUSY cleared after TX DONE"
            );


            // Clear tx_done
            @(negedge clk);

            tx_done = 1'b0;

            @(posedge clk);
            #1;

            check(
                tx_start === 1'b0,
                "TX START remains idle"
            );

        end

    endtask


    // ============================================================
    // MAIN TEST
    // ============================================================

    initial begin

        clk = 1'b0;
        rst = 1'b1;

        result_valid = 1'b0;
        classification = 1'b0;

        tx_busy = 1'b0;
        tx_done = 1'b0;

        pass_count = 0;
        fail_count = 0;


        // --------------------------------------------------------
        // RESET
        // --------------------------------------------------------

        #20;

        @(negedge clk);
        rst = 1'b0;


        // --------------------------------------------------------
        // TEST 1
        // classification = 0
        // --------------------------------------------------------

        test_result(
            1'b0,
            8'h00
        );


        // --------------------------------------------------------
        // TEST 2
        // classification = 1
        // --------------------------------------------------------

        test_result(
            1'b1,
            8'h01
        );


        // --------------------------------------------------------
        // TEST 3
        // Result arrives while TX is already busy
        // --------------------------------------------------------

        $display("");
        $display("----------------------------------------------");
        $display("TEST RESULT WHILE TX BUSY");
        $display("----------------------------------------------");

        tx_busy = 1'b1;
        tx_done = 1'b0;


        // Send result
        @(negedge clk);

        classification = 1'b1;
        result_valid = 1'b1;

        @(negedge clk);

        result_valid = 1'b0;


        // Allow controller to capture result
        @(posedge clk);
        #1;

        check(
            busy === 1'b1,
            "Controller BUSY while waiting for TX"
        );

        check(
            tx_data === 8'h01,
            "TX DATA retained while TX busy"
        );

        check(
            tx_start === 1'b0,
            "TX START waits for TX idle"
        );


        // --------------------------------------------------------
        // TX becomes idle
        // --------------------------------------------------------

        @(negedge clk);

        tx_busy = 1'b0;


        // Controller should generate tx_start on next clock
        @(posedge clk);
        #1;

        check(
            tx_start === 1'b1,
            "TX START asserted after TX idle"
        );


        // --------------------------------------------------------
        // UART accepts request
        // --------------------------------------------------------

        @(negedge clk);

        tx_busy = 1'b1;

        @(posedge clk);
        #1;

        check(
            tx_start === 1'b0,
            "TX START deasserted"
        );


        // --------------------------------------------------------
        // Finish transmission
        // --------------------------------------------------------

        @(negedge clk);

        tx_busy = 1'b0;
        tx_done = 1'b1;

        @(posedge clk);
        #1;

        check(
            busy === 1'b0,
            "Controller returns IDLE"
        );


        @(negedge clk);

        tx_done = 1'b0;


        // --------------------------------------------------------
        // FINAL RESULT
        // --------------------------------------------------------

        #20;

        $display("");
        $display("==============================================");
        $display("PASS = %0d", pass_count);
        $display("FAIL = %0d", fail_count);
        $display("==============================================");

        if (fail_count == 0)
            $display("UART CONTROLLER TEST PASSED");
        else
            $display("UART CONTROLLER TEST FAILED");

        $finish;

    end

endmodule