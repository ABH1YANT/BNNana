//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/27/2026 04:55:55 PM
// Design Name: 
// Module Name: controller_fsm
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

module controller_fsm (
    input  wire clk,
    input  wire rst,

    input  wire start,
    input  wire inference_done,

    output reg inference_start,
    output reg busy,
    output reg result_valid
);

    // ============================================================
    // STATE ENCODING
    // ============================================================

    localparam STATE_IDLE  = 2'd0;
    localparam STATE_START = 2'd1;
    localparam STATE_RUN   = 2'd2;
    localparam STATE_DONE  = 2'd3;

    reg [1:0] state;


    // ============================================================
    // STATE REGISTER
    // ============================================================

    always @(posedge clk) begin

        if (rst)
            state <= STATE_IDLE;

        else begin

            case (state)

                // ------------------------------------------------
                // Wait for a complete packet
                // ------------------------------------------------

                STATE_IDLE: begin

                    if (start)
                        state <= STATE_START;

                    else
                        state <= STATE_IDLE;

                end


                // ------------------------------------------------
                // Generate one-clock inference_start pulse
                // ------------------------------------------------

                STATE_START: begin
                    state <= STATE_RUN;
                end


                // ------------------------------------------------
                // Wait for inference_core
                // ------------------------------------------------

                STATE_RUN: begin

                    if (inference_done)
                        state <= STATE_DONE;

                    else
                        state <= STATE_RUN;

                end


                // ------------------------------------------------
                // Generate one-clock result_valid pulse
                // ------------------------------------------------

                STATE_DONE: begin
                    state <= STATE_IDLE;
                end


                // ------------------------------------------------
                // Safety
                // ------------------------------------------------

                default: begin
                    state <= STATE_IDLE;
                end

            endcase

        end

    end


    // ============================================================
    // OUTPUT LOGIC
    // ============================================================

    always @(*) begin

        // Default values
        inference_start = 1'b0;
        busy            = 1'b0;
        result_valid    = 1'b0;


        case (state)

            // ----------------------------------------------------
            // IDLE
            // ----------------------------------------------------

            STATE_IDLE: begin

                inference_start = 1'b0;
                busy            = 1'b0;
                result_valid    = 1'b0;

            end


            // ----------------------------------------------------
            // START
            //
            // inference_start is HIGH for exactly one clock.
            // ----------------------------------------------------

            STATE_START: begin

                inference_start = 1'b1;
                busy            = 1'b1;
                result_valid    = 1'b0;

            end


            // ----------------------------------------------------
            // RUN
            //
            // Wait for inference_core to finish.
            // ----------------------------------------------------

            STATE_RUN: begin

                inference_start = 1'b0;
                busy            = 1'b1;
                result_valid    = 1'b0;

            end


            // ----------------------------------------------------
            // DONE
            //
            // result_valid is HIGH for exactly one clock.
            // ----------------------------------------------------

            STATE_DONE: begin

                inference_start = 1'b0;
                busy            = 1'b0;
                result_valid    = 1'b1;

            end


            // ----------------------------------------------------
            // DEFAULT
            // ----------------------------------------------------

            default: begin

                inference_start = 1'b0;
                busy            = 1'b0;
                result_valid    = 1'b0;

            end

        endcase

    end

endmodule