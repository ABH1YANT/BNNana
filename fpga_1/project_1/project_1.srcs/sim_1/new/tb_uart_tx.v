`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/28/2026 12:57:55 AM
// Design Name: 
// Module Name: tb_uart_tx
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

module tb_uart_tx;

    reg        clk;
    reg        rst;

    reg [7:0]  tx_data;
    reg        tx_start;

    wire       tx;
    wire       busy;
    wire       tx_done;

    integer pass_count;
    integer fail_count;

    localparam CLK_FREQ      = 10_000_000;
    localparam BAUD_RATE     = 1_000_000;
    localparam CLKS_PER_BIT  = 10;


    uart_tx #(
        .CLK_FREQ(CLK_FREQ),
        .BAUD_RATE(BAUD_RATE)
    ) dut (
        .clk(clk),
        .rst(rst),
        .tx_data(tx_data),
        .tx_start(tx_start),
        .tx(tx),
        .busy(busy),
        .tx_done(tx_done)
    );


    always #5 clk = ~clk;


    // ------------------------------------------------------------
    // Wait one UART bit
    // ------------------------------------------------------------

    task wait_bit;

        integer i;

        begin

            for (i = 0; i < CLKS_PER_BIT; i = i + 1)
                @(posedge clk);

        end

    endtask


    // ------------------------------------------------------------
    // Check one byte
    // ------------------------------------------------------------

    task check_byte;

        input [7:0] expected_data;

        integer i;
        integer done_seen;

        begin

            done_seen = 0;

            $display("");
            $display("TRANSMITTING = %h", expected_data);


            // ----------------------------------------------------
            // Start transmission
            // ----------------------------------------------------

            @(negedge clk);

            tx_data  = expected_data;
            tx_start = 1'b1;

            @(negedge clk);

            tx_start = 1'b0;


            // ----------------------------------------------------
            // Start bit
            // ----------------------------------------------------

            @(negedge clk);

            if (tx === 1'b0) begin

                $display("START BIT: PASS");
                pass_count = pass_count + 1;

            end
            else begin

                $display("START BIT: FAIL");
                fail_count = fail_count + 1;

            end


            wait_bit;


            // ----------------------------------------------------
            // Data bits
            // ----------------------------------------------------

            for (i = 0; i < 8; i = i + 1) begin

                @(negedge clk);

                if (tx === expected_data[i]) begin

                    $display(
                        "DATA BIT %0d: PASS = %b",
                        i,
                        tx
                    );

                    pass_count = pass_count + 1;

                end
                else begin

                    $display(
                        "DATA BIT %0d: FAIL = %b EXPECTED=%b",
                        i,
                        tx,
                        expected_data[i]
                    );

                    fail_count = fail_count + 1;

                end

                wait_bit;

            end


            // ----------------------------------------------------
            // Stop bit
            // ----------------------------------------------------

            @(negedge clk);

            if (tx === 1'b1) begin

                $display("STOP BIT: PASS");
                pass_count = pass_count + 1;

            end
            else begin

                $display("STOP BIT: FAIL");
                fail_count = fail_count + 1;

            end


            // ----------------------------------------------------
            // Wait for TX DONE
            //
            // tx_done is only one clock wide, so monitor it
            // on every positive clock edge.
            // ----------------------------------------------------

            for (i = 0; i < CLKS_PER_BIT + 2; i = i + 1) begin

                @(posedge clk);

                if (tx_done === 1'b1)
                    done_seen = 1;

            end


            if (done_seen == 1) begin

                $display("TX DONE: PASS");
                pass_count = pass_count + 1;

            end
            else begin

                $display("TX DONE: FAIL");
                fail_count = fail_count + 1;

            end


            // ----------------------------------------------------
            // TX should be idle
            // ----------------------------------------------------

            if (tx === 1'b1) begin

                $display("IDLE TX: PASS");
                pass_count = pass_count + 1;

            end
            else begin

                $display("IDLE TX: FAIL");
                fail_count = fail_count + 1;

            end

        end

    endtask


    // ------------------------------------------------------------
    // Main
    // ------------------------------------------------------------

    initial begin

        clk      = 1'b0;
        rst      = 1'b1;

        tx_data  = 8'd0;
        tx_start = 1'b0;

        pass_count = 0;
        fail_count = 0;


        $display("");
        $display("==============================================");
        $display(" UART TX TEST");
        $display(" 8N1 / LSB FIRST");
        $display(" CLK = 10 MHz");
        $display(" BAUD = 1 MHz");
        $display("==============================================");
        $display("");


        // Reset

        #20;

        rst = 1'b0;

        #20;


        // Test bytes

        check_byte(8'hA5);

        check_byte(8'h3C);

        check_byte(8'h81);


        // --------------------------------------------------------
        // Final result
        // --------------------------------------------------------

        $display("");
        $display("==============================================");
        $display("PASS = %0d", pass_count);
        $display("FAIL = %0d", fail_count);
        $display("==============================================");

        if (fail_count == 0)
            $display("UART TX TEST PASSED");
        else
            $display("UART TX TEST FAILED");

        $display("");

        #20;

        $finish;

    end

endmodule