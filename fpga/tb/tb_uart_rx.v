`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/24/2026 12:28:10 AM
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



module tb_uart_rx();

    parameter CLKS_PER_BIT = 868;
    parameter CLK_PERIOD = 10; 

    reg clk;
    reg rst;
    reg rx;
    wire [7:0] rx_data;
    wire rx_valid;

    uart_rx #(
        .CLKS_PER_BIT(CLKS_PER_BIT)
    ) uut (
        .clk(clk),
        .rst(rst),
        .rx(rx),
        .rx_data(rx_data),
        .rx_valid(rx_valid)
    );

    always #(CLK_PERIOD/2) clk = ~clk;

    task send_byte;
        input [7:0] data;
        integer i;
        begin
            rx = 1'b0;
            #(CLK_PERIOD * CLKS_PER_BIT);
            
            for (i = 0; i < 8; i = i + 1) begin
                rx = data[i];
                #(CLK_PERIOD * CLKS_PER_BIT);
            end
            
            rx = 1'b1;
            #(CLK_PERIOD * CLKS_PER_BIT);
        end
    endtask

    initial begin
        clk = 0;
        rst = 1;
        rx = 1; 

        #100;
        rst = 0;
        #100;

        $display("--- Starting UART RX Simulation ---");

        // Test 1: Send 0xAA
        $display("Sending Byte: 0xAA");
        fork
            send_byte(8'hAA); // Thread 1: Sends the byte
            begin
                @(posedge rx_valid); // Thread 2: Listens for the pulse at the same time
                $display("Received Byte: 0x%h | Expected: 0xAA", rx_data);
            end
        join

        #1000; 

        // Test 2: Send 0x55
        $display("Sending Byte: 0x55");
        fork
            send_byte(8'h55);
            begin
                @(posedge rx_valid);
                $display("Received Byte: 0x%h | Expected: 0x55", rx_data);
            end
        join

        #1000;
        $display("--- Simulation Complete ---");
        $finish;
    end

endmodule
