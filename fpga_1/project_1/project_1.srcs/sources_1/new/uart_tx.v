`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/28/2026 12:56:39 AM
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

`timescale 1ns / 1ps

module uart_tx #(
    parameter CLK_FREQ  = 100_000_000,
    parameter BAUD_RATE = 115200
)(
    input  wire       clk,
    input  wire       rst,

    input  wire [7:0] tx_data,
    input  wire       tx_start,

    output reg        tx,
    output reg        busy,
    output reg        tx_done
);

    localparam integer CLKS_PER_BIT = CLK_FREQ / BAUD_RATE;

    localparam [2:0]
        S_IDLE  = 3'd0,
        S_START = 3'd1,
        S_DATA  = 3'd2,
        S_STOP  = 3'd3;

    reg [2:0] state;

    reg [15:0] clk_count;
    reg [2:0]  bit_index;

    reg [7:0] data_reg;


    always @(posedge clk) begin

        if (rst) begin

            state     <= S_IDLE;
            clk_count <= 16'd0;
            bit_index <= 3'd0;
            data_reg  <= 8'd0;

            tx        <= 1'b1;
            busy      <= 1'b0;
            tx_done   <= 1'b0;

        end
        else begin

            // tx_done is a one-clock pulse
            tx_done <= 1'b0;

            case (state)

                // ------------------------------------------------
                // IDLE
                // ------------------------------------------------

                S_IDLE: begin

                    tx        <= 1'b1;
                    busy      <= 1'b0;
                    clk_count <= 16'd0;
                    bit_index <= 3'd0;

                    if (tx_start) begin

                        data_reg  <= tx_data;

                        tx        <= 1'b0;
                        busy      <= 1'b1;

                        clk_count <= 16'd0;

                        state <= S_START;

                    end

                end


                // ------------------------------------------------
                // START BIT
                // ------------------------------------------------

                S_START: begin

                    tx   <= 1'b0;
                    busy <= 1'b1;

                    if (clk_count == CLKS_PER_BIT - 1) begin

                        clk_count <= 16'd0;
                        bit_index <= 3'd0;

                        tx <= data_reg[0];

                        state <= S_DATA;

                    end
                    else begin

                        clk_count <= clk_count + 1'b1;

                    end

                end


                // ------------------------------------------------
                // DATA BITS
                // LSB first
                // ------------------------------------------------

                S_DATA: begin

                    busy <= 1'b1;

                    if (clk_count == CLKS_PER_BIT - 1) begin

                        clk_count <= 16'd0;

                        if (bit_index == 3'd7) begin

                            tx <= 1'b1;

                            state <= S_STOP;

                        end
                        else begin

                            bit_index <= bit_index + 1'b1;

                            tx <= data_reg[bit_index + 1'b1];

                        end

                    end
                    else begin

                        clk_count <= clk_count + 1'b1;

                    end

                end


                // ------------------------------------------------
                // STOP BIT
                // ------------------------------------------------

                S_STOP: begin

                    tx   <= 1'b1;
                    busy <= 1'b1;

                    if (clk_count == CLKS_PER_BIT - 1) begin

                        clk_count <= 16'd0;

                        busy    <= 1'b0;
                        tx_done <= 1'b1;

                        state <= S_IDLE;

                    end
                    else begin

                        clk_count <= clk_count + 1'b1;

                    end

                end


                default: begin

                    state <= S_IDLE;
                    tx    <= 1'b1;
                    busy  <= 1'b0;

                end

            endcase

        end

    end

endmodule
