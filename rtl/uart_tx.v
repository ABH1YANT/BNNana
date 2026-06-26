`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/24/2026 12:55:01 AM
// Design Name: 
// Module Name: uart_tx
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


module uart_tx #(
    parameter CLKS_PER_BIT = 868
)(
    input wire clk,
    input wire rst,
    input wire [7:0] tx_data,
    input wire tx_start,
    output wire tx,
    output wire tx_busy
);

    localparam IDLE     = 3'b000;
    localparam TX_START = 3'b001;
    localparam TX_DATA  = 3'b010;
    localparam TX_STOP  = 3'b011;

    reg [2:0] state;
    reg [9:0] clk_count;
    reg [2:0] bit_index;
    reg [7:0] data_reg;
    reg tx_reg;
    reg busy_reg;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state <= IDLE;
            clk_count <= 0;
            bit_index <= 0;
            data_reg <= 0;
            tx_reg <= 1'b1; // TX line is high when idle
            busy_reg <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    tx_reg <= 1'b1;
                    clk_count <= 0;
                    bit_index <= 0;
                    
                    if (tx_start == 1'b1) begin
                        data_reg <= tx_data; // Latch the data
                        busy_reg <= 1'b1;    // Raise busy flag
                        state <= TX_START;
                    end else begin
                        busy_reg <= 1'b0;
                    end
                end

                TX_START: begin
                    tx_reg <= 1'b0; // Send Start Bit (0)
                    if (clk_count < CLKS_PER_BIT - 1) begin
                        clk_count <= clk_count + 1;
                    end else begin
                        clk_count <= 0;
                        state <= TX_DATA;
                    end
                end

                TX_DATA: begin
                    tx_reg <= data_reg[bit_index]; // Send Data Bit
                    if (clk_count < CLKS_PER_BIT - 1) begin
                        clk_count <= clk_count + 1;
                    end else begin
                        clk_count <= 0;
                        if (bit_index < 7) begin
                            bit_index <= bit_index + 1;
                        end else begin
                            bit_index <= 0;
                            state <= TX_STOP;
                        end
                    end
                end

                TX_STOP: begin
                    tx_reg <= 1'b1; // Send Stop Bit (1)
                    if (clk_count < CLKS_PER_BIT - 1) begin
                        clk_count <= clk_count + 1;
                    end else begin
                        clk_count <= 0;
                        busy_reg <= 1'b0; // Drop busy flag
                        state <= IDLE;
                    end
                end
                
                default: state <= IDLE;
            endcase
        end
    end

    assign tx = tx_reg;
    assign tx_busy = busy_reg;

endmodule
