`timescale 1ns / 1ps
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

    output reg  inference_start,
    output reg  busy,
    output reg  result_valid
);

    // ------------------------------------------------------------
    // State encoding
    // ------------------------------------------------------------

    localparam STATE_IDLE = 2'd0;
    localparam STATE_RUN  = 2'd1;
    localparam STATE_DONE = 2'd2;

    reg [1:0] state;
    reg [1:0] next_state;

    // ------------------------------------------------------------
    // State register
    // ------------------------------------------------------------

    always @(posedge clk) begin
        if (rst)
            state <= STATE_IDLE;
        else
            state <= next_state;
    end

    // ------------------------------------------------------------
    // Next-state logic
    // ------------------------------------------------------------

    always @(*) begin

        next_state = state;

        case (state)

            STATE_IDLE: begin
                if (start)
                    next_state = STATE_RUN;
            end

            STATE_RUN: begin
                if (inference_done)
                    next_state = STATE_DONE;
            end

            STATE_DONE: begin
                if (!start)
                    next_state = STATE_IDLE;
            end

            default: begin
                next_state = STATE_IDLE;
            end

        endcase
    end

    // ------------------------------------------------------------
    // Output logic
    // ------------------------------------------------------------

    always @(*) begin

        inference_start = 1'b0;
        busy            = 1'b0;
        result_valid    = 1'b0;

        case (state)

            STATE_IDLE: begin
                // Waiting for a new inference request
            end

            STATE_RUN: begin
                busy = 1'b1;

                // Start pulse occurs while entering/running
                inference_start = 1'b1;

                // If inference is already complete,
                // controller will transition to DONE.
            end

            STATE_DONE: begin
                result_valid = 1'b1;
            end

            default: begin
                inference_start = 1'b0;
                busy            = 1'b0;
                result_valid    = 1'b0;
            end

        endcase
    end

endmodule