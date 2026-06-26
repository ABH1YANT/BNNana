`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/24/2026 12:55:44 AM
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


module tb_uart_tx();

    parameter CLKS_PER_BIT = 868;
    parameter CLK_PERIOD = 10; 

    reg clk;
    reg rst;
    reg [7:0] tx_data;
    reg tx_start;
    wire tx;
    wire tx_busy;

    // Instantiate the Unit Under Test (UUT)
    uart_tx #(
        .CLKS_PER_BIT(CLKS_PER_BIT)
    ) uut (
        .clk(clk),
        .rst(rst),
        .tx_data(tx_data),
        .tx_start(tx_start),
        .tx(tx),
        .tx_busy(tx_busy)
    );

    // Generate 100 MHz Clock
    always #(CLK_PERIOD/2) clk = ~clk;

    // Task to simulate the PC receiving a byte
    reg [7:0] received_byte;
    task receive_byte;
        integer i;
        begin
            // Wait for Start Bit (tx goes to 0)
            @(negedge tx);
            
            // Wait half a bit to sample in the middle
            #(CLK_PERIOD * (CLKS_PER_BIT / 2));
            
            // Wait a full bit to reach the first data bit
            #(CLK_PERIOD * CLKS_PER_BIT);
            
            // Sample 8 data bits
            for (i = 0; i < 8; i = i + 1) begin
                received_byte[i] = tx;
                #(CLK_PERIOD * CLKS_PER_BIT);
            end
            
            // Wait for Stop Bit
            #(CLK_PERIOD * CLKS_PER_BIT);
        end
    endtask

    initial begin
        // Initialize Inputs
        clk = 0;
        rst = 1;
        tx_data = 0;
        tx_start = 0;

        #100;
        rst = 0;
        #100;

        $display("--- Starting UART TX Simulation ---");

        // Test 1: Send 0x55 (Benign / Alternating bits)
        $display("Telling FPGA to send: 0x55");
        tx_data = 8'h55;
        tx_start = 1;
        #CLK_PERIOD; // Pulse start for 1 clock cycle
        tx_start = 0;

        // Call the PC receiver task to listen to the tx wire
        receive_byte();
        $display("PC Received: 0x%h | Expected: 0x55", received_byte);

        #1000;

        // Test 2: Send 0x01 (DDoS Detected)
        $display("Telling FPGA to send: 0x01");
        tx_data = 8'h01;
        tx_start = 1;
        #CLK_PERIOD;
        tx_start = 0;

        receive_byte();
        $display("PC Received: 0x%h | Expected: 0x01", received_byte);

        #1000;
        $display("--- Simulation Complete ---");
        $finish;
    end

endmodule
