`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/27/2026 06:08:38 PM
// Design Name: 
// Module Name: tb_uart_rx
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

module tb_uart_rx;

    // ------------------------------------------------------------
    // Use a small simulated clock so simulation is fast
    // ------------------------------------------------------------

    localparam CLK_FREQ  = 10_000_000;
    localparam BAUD_RATE = 1_000_000;

    localparam CLKS_PER_BIT = CLK_FREQ / BAUD_RATE;

    reg clk;
    reg rst;
    reg rx;

    wire [7:0] rx_data;
    wire       rx_valid;
    wire       busy;

    integer pass_count;
    integer fail_count;

    // ------------------------------------------------------------
    // DUT
    // ------------------------------------------------------------

    uart_rx #(
        .CLK_FREQ(CLK_FREQ),
        .BAUD_RATE(BAUD_RATE)
    ) dut (
        .clk(clk),
        .rst(rst),
        .rx(rx),
        .rx_data(rx_data),
        .rx_valid(rx_valid),
        .busy(busy)
    );

    // ------------------------------------------------------------
    // Clock
    // 10 MHz = 100 ns period
    // ------------------------------------------------------------

    always #50 clk = ~clk;

    // ------------------------------------------------------------
    // UART transmit task
    //
    // Sends one 8N1 byte.
    // ------------------------------------------------------------

    task uart_send_byte;

        input [7:0] data;
        integer i;

        begin

            // Idle
            rx = 1'b1;

            // Start bit
            #(CLKS_PER_BIT * 100);
            rx = 1'b0;

            // Data bits, LSB first
            for (i = 0; i < 8; i = i + 1) begin

                #(CLKS_PER_BIT * 100);
                rx = data[i];

            end

            // Stop bit
            #(CLKS_PER_BIT * 100);
            rx = 1'b1;

            // Return to idle
            #(CLKS_PER_BIT * 100);

        end

    endtask

    // ------------------------------------------------------------
    // Wait for received byte
    // ------------------------------------------------------------

    task check_byte;

        input [7:0] expected;
        input integer test_number;

        begin

            wait (rx_valid == 1'b1);

            #1;

            if (rx_data === expected) begin

                $display(
                    "TEST %0d: PASS RX=%02h",
                    test_number,
                    rx_data
                );

                pass_count = pass_count + 1;

            end
            else begin

                $display(
                    "TEST %0d: FAIL RX=%02h EXPECTED=%02h",
                    test_number,
                    rx_data,
                    expected
                );

                fail_count = fail_count + 1;

            end

        end

    endtask

    // ------------------------------------------------------------
    // Main test
    // ------------------------------------------------------------

    initial begin

        clk = 1'b0;
        rst = 1'b1;
        rx  = 1'b1;

        pass_count = 0;
        fail_count = 0;

        $display("");
        $display("==============================================");
        $display(" UART RX TEST");
        $display(" 8N1");
        $display("==============================================");
        $display("");

        // Reset
        #500;

        rst = 1'b0;

        #500;

        // --------------------------------------------------------
        // Test 1
        // --------------------------------------------------------

        fork
            uart_send_byte(8'hA5);
            check_byte(8'hA5, 1);
        join

        // --------------------------------------------------------
        // Test 2
        // --------------------------------------------------------

        fork
            uart_send_byte(8'h3C);
            check_byte(8'h3C, 2);
        join

        // --------------------------------------------------------
        // Test 3
        // --------------------------------------------------------

        fork
            uart_send_byte(8'h00);
            check_byte(8'h00, 3);
        join

        // --------------------------------------------------------
        // Test 4
        // --------------------------------------------------------

        fork
            uart_send_byte(8'hFF);
            check_byte(8'hFF, 4);
        join

        // --------------------------------------------------------
        // Test 5
        // --------------------------------------------------------

        fork
            uart_send_byte(8'h81);
            check_byte(8'h81, 5);
        join

        // --------------------------------------------------------
        // Test 6
        // --------------------------------------------------------

        fork
            uart_send_byte(8'h7E);
            check_byte(8'h7E, 6);
        join

        // --------------------------------------------------------
        // Summary
        // --------------------------------------------------------

        $display("");
        $display("==============================================");
        $display("PASS = %0d", pass_count);
        $display("FAIL = %0d", fail_count);
        $display("==============================================");

        if (fail_count == 0)
            $display("UART RX TEST PASSED");
        else
            $display("UART RX TEST FAILED");

        $display("");

        #100000;
        $finish;

    end

endmodule
