`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/28/2026 08:28:13 AM
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

`timescale 1ns / 1ps

module uart_controller (
    input  wire       clk,
    input  wire       rst,

    // Inference result interface
    input  wire       result_valid,
    input  wire       classification,

    // UART TX interface
    output reg  [7:0] tx_data,
    output reg        tx_start,
    input  wire       tx_busy,
    input  wire       tx_done,

    // Controller status
    output reg        busy
);

    localparam S_IDLE = 2'd0;
    localparam S_SEND = 2'd1;
    localparam S_WAIT = 2'd2;

    reg [1:0] state;

    always @(posedge clk) begin
        if (rst) begin
            state   <= S_IDLE;
            tx_data <= 8'd0;
            tx_start <= 1'b0;
            busy    <= 1'b0;
        end
        else begin
            // tx_start is a one-cycle pulse
            tx_start <= 1'b0;

            case (state)

                // --------------------------------------------------
                // Wait for a completed inference
                // --------------------------------------------------
                S_IDLE: begin
                    busy <= 1'b0;

                    if (result_valid) begin
                        if (classification)
                            tx_data <= 8'h01;
                        else
                            tx_data <= 8'h00;

                        busy  <= 1'b1;
                        state <= S_SEND;
                    end
                end

                // --------------------------------------------------
                // Start UART transmission
                // --------------------------------------------------
                S_SEND: begin
                    busy <= 1'b1;

                    if (!tx_busy) begin
                        tx_start <= 1'b1;
                        state <= S_WAIT;
                    end
                end

                // --------------------------------------------------
                // Wait until UART TX finishes
                // --------------------------------------------------
                S_WAIT: begin
                    busy <= 1'b1;

                    if (tx_done) begin
                        busy  <= 1'b0;
                        state <= S_IDLE;
                    end
                end

                default: begin
                    state <= S_IDLE;
                    busy  <= 1'b0;
                    tx_start <= 1'b0;
                end

            endcase
        end
    end

endmodule