`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/28/2026 12:47:24 AM
// Design Name: 
// Module Name: packet_parser
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

module packet_parser (

    input  wire        clk,
    input  wire        rst,

    input  wire [7:0]  rx_data,
    input  wire        rx_valid,

    output reg  [3:0]  feature_index,
    output reg  [26:0] feature_in,
    output reg         feature_valid,

    output reg         packet_done,
    output reg         packet_error
);

    localparam [7:0] HEADER = 8'hAA;
    localparam [7:0] FOOTER = 8'h55;

    localparam S_IDLE    = 2'd0;
    localparam S_PAYLOAD = 2'd1;
    localparam S_FOOTER  = 2'd2;

    reg [1:0] state;

    reg [5:0] byte_count;

    reg [7:0] b0;
    reg [7:0] b1;
    reg [7:0] b2;

    always @(posedge clk) begin

        if (rst) begin

            state         <= S_IDLE;
            byte_count    <= 6'd0;

            b0            <= 8'd0;
            b1            <= 8'd0;
            b2            <= 8'd0;

            feature_index <= 4'd0;
            feature_in    <= 27'd0;

            feature_valid <= 1'b0;
            packet_done   <= 1'b0;
            packet_error  <= 1'b0;

        end
        else begin

            // Default: pulses are one clock wide
            feature_valid <= 1'b0;
            packet_done   <= 1'b0;
            packet_error  <= 1'b0;

            if (rx_valid) begin

                case (state)

                    // =================================================
                    // WAIT FOR HEADER
                    // =================================================

                    S_IDLE: begin

                        if (rx_data == HEADER) begin
                            byte_count <= 6'd0;
                            state <= S_PAYLOAD;
                        end

                    end


                    // =================================================
                    // RECEIVE 43 PAYLOAD BYTES
                    // =================================================

                    S_PAYLOAD: begin

                        case (byte_count)

                            // -----------------------------------------
                            // F0 = 14 bits = 2 bytes
                            // byte0 = bits [7:0]
                            // byte1 = bits [13:8]
                            // -----------------------------------------

                            6'd0: begin
                                b0 <= rx_data;
                            end

                            6'd1: begin
                                feature_index <= 4'd0;
                                feature_in <= {
                                    13'd0,
                                    rx_data[5:0],
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F1 = 11 bits = 2 bytes
                            // -----------------------------------------

                            6'd2: begin
                                b0 <= rx_data;
                            end

                            6'd3: begin
                                feature_index <= 4'd1;
                                feature_in <= {
                                    16'd0,
                                    rx_data[2:0],
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F2 = 25 bits = 4 bytes
                            // -----------------------------------------

                            6'd4: b0 <= rx_data;
                            6'd5: b1 <= rx_data;
                            6'd6: b2 <= rx_data;

                            6'd7: begin
                                feature_index <= 4'd2;
                                feature_in <= {
                                    2'd0,
                                    rx_data[0],
                                    b2,
                                    b1,
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F3 = 25 bits = 4 bytes
                            // -----------------------------------------

                            6'd8:  b0 <= rx_data;
                            6'd9:  b1 <= rx_data;
                            6'd10: b2 <= rx_data;

                            6'd11: begin
                                feature_index <= 4'd3;
                                feature_in <= {
                                    2'd0,
                                    rx_data[0],
                                    b2,
                                    b1,
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F4 = 16 bits = 2 bytes
                            // -----------------------------------------

                            6'd12: b0 <= rx_data;

                            6'd13: begin
                                feature_index <= 4'd4;
                                feature_in <= {
                                    11'd0,
                                    rx_data,
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F5 = 11 bits = 2 bytes
                            // -----------------------------------------

                            6'd14: b0 <= rx_data;

                            6'd15: begin
                                feature_index <= 4'd5;
                                feature_in <= {
                                    16'd0,
                                    rx_data[2:0],
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F6 = 1 bit = 1 byte
                            // -----------------------------------------

                            6'd16: begin
                                feature_index <= 4'd6;
                                feature_in <= {
                                    26'd0,
                                    rx_data[0]
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F7 = 17 bits = 3 bytes
                            // -----------------------------------------

                            6'd17: b0 <= rx_data;
                            6'd18: b1 <= rx_data;

                            6'd19: begin
                                feature_index <= 4'd7;
                                feature_in <= {
                                    10'd0,
                                    rx_data[0],
                                    b1,
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F8 = 15 bits = 2 bytes
                            // -----------------------------------------

                            6'd20: b0 <= rx_data;

                            6'd21: begin
                                feature_index <= 4'd8;
                                feature_in <= {
                                    12'd0,
                                    rx_data[6:0],
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F9 = 17 bits = 3 bytes
                            // -----------------------------------------

                            6'd22: b0 <= rx_data;
                            6'd23: b1 <= rx_data;

                            6'd24: begin
                                feature_index <= 4'd9;
                                feature_in <= {
                                    10'd0,
                                    rx_data[0],
                                    b1,
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F10 = 21 bits = 3 bytes
                            // -----------------------------------------

                            6'd25: b0 <= rx_data;
                            6'd26: b1 <= rx_data;

                            6'd27: begin
                                feature_index <= 4'd10;
                                feature_in <= {
                                    6'd0,
                                    rx_data[4:0],
                                    b1,
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F11 = 15 bits = 2 bytes
                            // -----------------------------------------

                            6'd28: b0 <= rx_data;

                            6'd29: begin
                                feature_index <= 4'd11;
                                feature_in <= {
                                    12'd0,
                                    rx_data[6:0],
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F12 = 21 bits = 3 bytes
                            // -----------------------------------------

                            6'd30: b0 <= rx_data;
                            6'd31: b1 <= rx_data;

                            6'd32: begin
                                feature_index <= 4'd12;
                                feature_in <= {
                                    6'd0,
                                    rx_data[4:0],
                                    b1,
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F13 = 21 bits = 3 bytes
                            // -----------------------------------------

                            6'd33: b0 <= rx_data;
                            6'd34: b1 <= rx_data;

                            6'd35: begin
                                feature_index <= 4'd13;
                                feature_in <= {
                                    6'd0,
                                    rx_data[4:0],
                                    b1,
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F14 = 27 bits = 4 bytes
                            // -----------------------------------------

                            6'd36: b0 <= rx_data;
                            6'd37: b1 <= rx_data;
                            6'd38: b2 <= rx_data;

                            6'd39: begin
                                feature_index <= 4'd14;
                                feature_in <= {
                                    rx_data[2:0],
                                    b2,
                                    b1,
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end


                            // -----------------------------------------
                            // F15 = 21 bits = 3 bytes
                            // -----------------------------------------

                            6'd40: b0 <= rx_data;
                            6'd41: b1 <= rx_data;

                            6'd42: begin
                                feature_index <= 4'd15;
                                feature_in <= {
                                    6'd0,
                                    rx_data[4:0],
                                    b1,
                                    b0
                                };
                                feature_valid <= 1'b1;
                            end

                            default: begin
                            end

                        endcase


                        if (byte_count == 6'd42) begin
                            state <= S_FOOTER;
                        end
                        else begin
                            byte_count <= byte_count + 1'b1;
                        end

                    end


                    // =================================================
                    // FOOTER
                    // =================================================

                    S_FOOTER: begin

                        if (rx_data == FOOTER) begin
                            packet_done <= 1'b1;
                        end
                        else begin
                            packet_error <= 1'b1;
                        end

                        state <= S_IDLE;
                        byte_count <= 6'd0;

                    end


                    default: begin
                        state <= S_IDLE;
                    end

                endcase

            end

        end
    end

endmodule