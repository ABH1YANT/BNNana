`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/24/2026 12:27:11 AM
// Design Name: 
// Module Name: uart_rx
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


module uart_rx #(
    // 100 MHz Clock / 115200 Baud Rate = 868 clock cycles per bit
    parameter CLKS_PER_BIT = 868
)(
    input wire clk,
    input wire rst,
    input wire rx,
    output wire [7:0] rx_data,
    output wire rx_valid
);

    // FSM States
    localparam IDLE     = 3'b000;
    localparam RX_START = 3'b001;
    localparam RX_DATA  = 3'b010;
    localparam RX_STOP  = 3'b011;
    localparam CLEANUP  = 3'b100;

    reg [2:0] state;
    reg [9:0] clk_count;   // Needs to count up to 868
    reg [2:0] bit_index;   // Needs to count 0 to 7 (8 bits)
    reg [7:0] rx_data_reg;
    reg rx_valid_reg;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state <= IDLE;
            clk_count <= 0;
            bit_index <= 0;
            rx_data_reg <= 0;
            rx_valid_reg <= 0;
        end else begin
            case (state)
                IDLE: begin
                    rx_valid_reg <= 0;
                    clk_count <= 0;
                    bit_index <= 0;
                    
                    if (rx == 1'b0) begin // Start bit detected
                        state <= RX_START;
                    end else begin
                        state <= IDLE;
                    end
                end

                RX_START: begin
                    // Wait for the middle of the start bit to sample safely
                    if (clk_count == (CLKS_PER_BIT / 2)) begin
                        if (rx == 1'b0) begin // Still 0? It's a valid start bit
                            clk_count <= 0;
                            state <= RX_DATA;
                        end else begin
                            state <= IDLE; // False alarm (glitch)
                        end
                    end else begin
                        clk_count <= clk_count + 1;
                        state <= RX_START;
                    end
                end

                RX_DATA: begin
                    // Wait a full bit duration
                    if (clk_count < CLKS_PER_BIT - 1) begin
                        clk_count <= clk_count + 1;
                        state <= RX_DATA;
                    end else begin
                        clk_count <= 0;
                        rx_data_reg[bit_index] <= rx; // Sample the bit
                        
                        if (bit_index < 7) begin
                            bit_index <= bit_index + 1;
                            state <= RX_DATA;
                        end else begin
                            bit_index <= 0;
                            state <= RX_STOP;
                        end
                    end
                end

                RX_STOP: begin
                    // Wait a full bit duration for the stop bit
                    if (clk_count < CLKS_PER_BIT - 1) begin
                        clk_count <= clk_count + 1;
                        state <= RX_STOP;
                    end else begin
                        rx_valid_reg <= 1'b1; // Pulse valid high for 1 clock cycle
                        clk_count <= 0;
                        state <= CLEANUP;
                    end
                end

                CLEANUP: begin
                    // Go back to IDLE and pull valid low
                    state <= IDLE;
                    rx_valid_reg <= 1'b0;
                end
                
                default: state <= IDLE;
            endcase
        end
    end

    // Assign internal registers to output wires
    assign rx_data = rx_data_reg;
    assign rx_valid = rx_valid_reg;

endmodule