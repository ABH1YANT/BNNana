`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/24/2026 01:36:13 AM
// Design Name: 
// Module Name: tb_uart_controller
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


module tb_uart_controller();

    parameter CLKS_PER_BIT = 868;
    parameter CLK_PERIOD = 10; 

    reg clk;
    reg rst;
    
    // Physical Pins
    reg rx;
    wire tx;
    
    // Internal Signals
    wire [7:0] rx_data;
    wire rx_valid;
    reg [7:0] tx_data;
    reg tx_start;
    wire tx_busy;

    // Instantiate the Unit Under Test (UUT)
    uart_controller #(
        .CLKS_PER_BIT(CLKS_PER_BIT)
    ) uut (
        .clk(clk),
        .rst(rst),
        .rx(rx),
        .tx(tx),
        .rx_data(rx_data),
        .rx_valid(rx_valid),
        .tx_data(tx_data),
        .tx_start(tx_start),
        .tx_busy(tx_busy)
    );

    // Generate 100 MHz Clock
    always #(CLK_PERIOD/2) clk = ~clk;

    // PC Simulator: Send Byte Task
    task send_byte;
        input [7:0] data;
        integer i;
        begin
            rx = 1'b0; // Start bit
            #(CLK_PERIOD * CLKS_PER_BIT);
            for (i = 0; i < 8; i = i + 1) begin
                rx = data[i];
                #(CLK_PERIOD * CLKS_PER_BIT);
            end
            rx = 1'b1; // Stop bit
            #(CLK_PERIOD * CLKS_PER_BIT);
        end
    endtask

    // PC Simulator: Receive Byte Task
    reg [7:0] received_byte;
    task receive_byte;
        integer i;
        begin
            @(negedge tx); // Wait for start bit
            #(CLK_PERIOD * (CLKS_PER_BIT / 2)); // Center of start bit
            #(CLK_PERIOD * CLKS_PER_BIT); // Move to first data bit
            for (i = 0; i < 8; i = i + 1) begin
                received_byte[i] = tx;
                #(CLK_PERIOD * CLKS_PER_BIT);
            end
            #(CLK_PERIOD * CLKS_PER_BIT); // Wait for stop bit
        end
    endtask

    initial begin
        // Initialize
        clk = 0;
        rst = 1;
        rx = 1;
        tx_data = 0;
        tx_start = 0;

        #100;
        rst = 0;
        #100;

        $display("--- Starting UART Controller Loopback Test ---");

        $display("PC: Sending 0x88 to FPGA...");
        
        // Step 1: PC sends, FPGA receives
        fork
            send_byte(8'h88); 
            begin
                @(posedge rx_valid); 
                $display("FPGA: Received 0x%h. Looping it back to PC...", rx_data);
            end
        join

        // Step 2: Now that the PC is done sending, tell the FPGA to transmit
        // AND tell the PC to listen at the exact same time.
        tx_data = rx_data;
        
        fork
            begin
                tx_start = 1;
                #CLK_PERIOD;
                tx_start = 0;
            end
            receive_byte(); // PC listens
        join

        $display("PC: Received 0x%h back from FPGA | Expected: 0x88", received_byte);

        #1000;
        $display("--- Simulation Complete ---");
        $finish;
    end

endmodule