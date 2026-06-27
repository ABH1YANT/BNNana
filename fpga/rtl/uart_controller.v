`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/24/2026 01:35:32 AM
// Design Name: 
// Module Name: uart_controller
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



module uart_controller #(
    parameter CLKS_PER_BIT = 868
)(
    input wire clk,
    input wire rst,
    
    // Physical FPGA Pins
    input wire rx,
    output wire tx,
    
    // Internal Interface to FPGA Logic (Receiver)
    output wire [7:0] rx_data,
    output wire rx_valid,
    
    // Internal Interface to FPGA Logic (Transmitter)
    input wire [7:0] tx_data,
    input wire tx_start,
    output wire tx_busy
);

    // Instantiate the Receiver
    uart_rx #(
        .CLKS_PER_BIT(CLKS_PER_BIT)
    ) rx_inst (
        .clk(clk),
        .rst(rst),
        .rx(rx),
        .rx_data(rx_data),
        .rx_valid(rx_valid)
    );

    // Instantiate the Transmitter
    uart_tx #(
        .CLKS_PER_BIT(CLKS_PER_BIT)
    ) tx_inst (
        .clk(clk),
        .rst(rst),
        .tx_data(tx_data),
        .tx_start(tx_start),
        .tx(tx),
        .tx_busy(tx_busy)
    );

endmodule
