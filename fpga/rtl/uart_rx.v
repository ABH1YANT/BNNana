`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/27/2026 06:07:59 PM
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
`timescale 1ns / 1ps

module uart_rx #(
    parameter CLK_FREQ  = 75_000_000,
    parameter BAUD_RATE = 115200
)(
    input  wire       clk,
    input  wire       rst,

    input  wire       rx,

    output reg [7:0]  rx_data,
    output reg        rx_valid,
    output reg        busy
);

    // ------------------------------------------------------------
    // UART timing
    // ------------------------------------------------------------

    localparam integer CLKS_PER_BIT = CLK_FREQ / BAUD_RATE;
    localparam integer HALF_BIT     = CLKS_PER_BIT / 2;

    // ------------------------------------------------------------
    // State machine
    // ------------------------------------------------------------

    localparam STATE_IDLE  = 2'd0;
    localparam STATE_START = 2'd1;
    localparam STATE_DATA  = 2'd2;
    localparam STATE_STOP  = 2'd3;

    reg [1:0] state;

    // ------------------------------------------------------------
    // Counters
    // ------------------------------------------------------------

    integer clk_count;
    integer bit_index;

    // ------------------------------------------------------------
    // Synchronize asynchronous UART input
    // ------------------------------------------------------------

    reg rx_sync1;
    reg rx_sync2;

    always @(posedge clk) begin
        if (rst) begin
            rx_sync1 <= 1'b1;
            rx_sync2 <= 1'b1;
        end
        else begin
            rx_sync1 <= rx;
            rx_sync2 <= rx_sync1;
        end
    end

    // ------------------------------------------------------------
    // UART receiver
    // ------------------------------------------------------------

    always @(posedge clk) begin

        if (rst) begin

            state     <= STATE_IDLE;

            clk_count <= 0;
            bit_index <= 0;

            rx_data   <= 8'd0;
            rx_valid  <= 1'b0;
            busy      <= 1'b0;

        end
        else begin

            // rx_valid is a one-clock pulse
            rx_valid <= 1'b0;

            case (state)

                // ------------------------------------------------
                // Wait for start bit
                // ------------------------------------------------

                STATE_IDLE: begin

                    busy      <= 1'b0;
                    clk_count <= 0;
                    bit_index <= 0;

                    // UART idle = 1
                    // Start bit = 0
                    if (rx_sync2 == 1'b0) begin

                        state     <= STATE_START;
                        busy      <= 1'b1;
                        clk_count <= 0;

                    end

                end

                // ------------------------------------------------
                // Verify middle of start bit
                // ------------------------------------------------

                STATE_START: begin

                    if (clk_count < HALF_BIT - 1) begin

                        clk_count <= clk_count + 1;

                    end
                    else begin

                        clk_count <= 0;

                        // Still low -> valid start bit
                        if (rx_sync2 == 1'b0) begin

                            state     <= STATE_DATA;
                            bit_index <= 0;

                        end
                        else begin

                            // False start
                            state <= STATE_IDLE;
                            busy  <= 1'b0;

                        end

                    end

                end

                // ------------------------------------------------
                // Receive 8 data bits
                // ------------------------------------------------

                STATE_DATA: begin

                    if (clk_count < CLKS_PER_BIT - 1) begin

                        clk_count <= clk_count + 1;

                    end
                    else begin

                        clk_count <= 0;

                        // LSB first
                        rx_data[bit_index] <= rx_sync2;

                        if (bit_index < 7) begin

                            bit_index <= bit_index + 1;

                        end
                        else begin

                            bit_index <= 0;
                            state     <= STATE_STOP;

                        end

                    end

                end

                // ------------------------------------------------
                // Receive stop bit
                // ------------------------------------------------

                STATE_STOP: begin

                    if (clk_count < CLKS_PER_BIT - 1) begin

                        clk_count <= clk_count + 1;

                    end
                    else begin

                        clk_count <= 0;

                        // Stop bit should be HIGH
                        if (rx_sync2 == 1'b1) begin

                            rx_valid <= 1'b1;

                        end

                        state <= STATE_IDLE;
                        busy  <= 1'b0;

                    end

                end

                default: begin

                    state     <= STATE_IDLE;
                    clk_count <= 0;
                    bit_index <= 0;
                    busy      <= 1'b0;

                end

            endcase

        end

    end

endmodule