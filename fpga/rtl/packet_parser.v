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

//////////////////////////////////////////////////////////////////////////////////
// Packet Parser
//
// UART packet format:
//
//   Byte 0       : 0xAA  - header
//   Bytes 1..43  : 43-byte payload
//   Byte 44      : 0x55  - footer
//
// Total packet size = 45 bytes
//
// Payload feature order:
//
//   0  Bwd Packet Length Max       - 14 bits  - 2 bytes
//   1  Min Packet Length           - 11 bits  - 2 bytes
//   2  Subflow Bwd Bytes           - 25 bits  - 4 bytes
//   3  Total Length Bwd Packets    - 25 bits  - 4 bytes
//   4  Destination Port            - 16 bits  - 2 bytes
//   5  min_seg_size_forward        - 11 bits  - 2 bytes
//   6  ACK Flag Count               - 1 bit   - 1 byte
//   7  Subflow Bwd Packets          - 17 bits  - 3 bytes
//   8  Fwd Packet Length Max       - 15 bits  - 2 bytes
//   9  Total Backward Packets       - 17 bits  - 3 bytes
//   10 Subflow Fwd Bytes            - 21 bits  - 3 bytes
//   11 Max Packet Length            - 15 bits  - 2 bytes
//   12 Total Length Fwd Packets     - 21 bits  - 3 bytes
//   13 Bwd Header Length            - 21 bits  - 3 bytes
//   14 Flow Duration                - 27 bits  - 4 bytes
//   15 Fwd Header Length            - 21 bits  - 3 bytes
//
// Byte ordering:
//   Little endian.
//   First byte received = least significant byte.
//
// feature_valid:
//   Pulses for one clock whenever a complete feature has been parsed.
//
// packet_done:
//   Pulses for one clock after a correct 0x55 footer.
//
// packet_error:
//   Pulses for one clock if the footer is incorrect.
//
//////////////////////////////////////////////////////////////////////////////////

module packet_parser (

    input wire        clk,
    input wire        rst,

    input wire [7:0]  rx_data,
    input wire        rx_valid,

    output reg [3:0]  feature_index,
    output reg [26:0] feature_in,

    output reg        feature_valid,
    output reg        packet_done,
    output reg        packet_error
);

    // ------------------------------------------------------------
    // Packet constants
    // ------------------------------------------------------------

    localparam [7:0] HEADER = 8'hAA;
    localparam [7:0] FOOTER = 8'h55;


    // ------------------------------------------------------------
    // Parser states
    // ------------------------------------------------------------

    localparam [1:0] S_IDLE    = 2'd0;
    localparam [1:0] S_PAYLOAD = 2'd1;
    localparam [1:0] S_FOOTER  = 2'd2;

    reg [1:0] state;


    // ------------------------------------------------------------
    // Payload byte counter
    //
    // 0..42 = 43 payload bytes
    // ------------------------------------------------------------

    reg [5:0] byte_count;


    // ------------------------------------------------------------
    // Temporary byte registers
    // ------------------------------------------------------------

    reg [7:0] b0;
    reg [7:0] b1;
    reg [7:0] b2;


    // ------------------------------------------------------------
    // Main parser
    // ------------------------------------------------------------

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

            // ----------------------------------------------------
            // These outputs are pulses.
            // ----------------------------------------------------

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
                            state      <= S_PAYLOAD;

                        end

                    end


                    // =================================================
                    // RECEIVE 43 PAYLOAD BYTES
                    // =================================================

                    S_PAYLOAD: begin

                        case (byte_count)

                            // -----------------------------------------
                            // Feature 0
                            // Bwd Packet Length Max
                            // 14 bits
                            // Bytes 0-1
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
                            // Feature 1
                            // Min Packet Length
                            // 11 bits
                            // Bytes 2-3
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
                            // Feature 2
                            // Subflow Bwd Bytes
                            // 25 bits
                            // Bytes 4-7
                            // -----------------------------------------

                            6'd4: begin
                                b0 <= rx_data;
                            end

                            6'd5: begin
                                b1 <= rx_data;
                            end

                            6'd6: begin
                                b2 <= rx_data;
                            end

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
                            // Feature 3
                            // Total Length of Bwd Packets
                            // 25 bits
                            // Bytes 8-11
                            // -----------------------------------------

                            6'd8: begin
                                b0 <= rx_data;
                            end

                            6'd9: begin
                                b1 <= rx_data;
                            end

                            6'd10: begin
                                b2 <= rx_data;
                            end

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
                            // Feature 4
                            // Destination Port
                            // 16 bits
                            // Bytes 12-13
                            // -----------------------------------------

                            6'd12: begin
                                b0 <= rx_data;
                            end

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
                            // Feature 5
                            // min_seg_size_forward
                            // 11 bits
                            // Bytes 14-15
                            // -----------------------------------------

                            6'd14: begin
                                b0 <= rx_data;
                            end

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
                            // Feature 6
                            // ACK Flag Count
                            // 1 bit
                            // Byte 16
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
                            // Feature 7
                            // Subflow Bwd Packets
                            // 17 bits
                            // Bytes 17-19
                            // -----------------------------------------

                            6'd17: begin
                                b0 <= rx_data;
                            end

                            6'd18: begin
                                b1 <= rx_data;
                            end

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
                            // Feature 8
                            // Fwd Packet Length Max
                            // 15 bits
                            // Bytes 20-21
                            // -----------------------------------------

                            6'd20: begin
                                b0 <= rx_data;
                            end

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
                            // Feature 9
                            // Total Backward Packets
                            // 17 bits
                            // Bytes 22-24
                            // -----------------------------------------

                            6'd22: begin
                                b0 <= rx_data;
                            end

                            6'd23: begin
                                b1 <= rx_data;
                            end

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
                            // Feature 10
                            // Subflow Fwd Bytes
                            // 21 bits
                            // Bytes 25-27
                            // -----------------------------------------

                            6'd25: begin
                                b0 <= rx_data;
                            end

                            6'd26: begin
                                b1 <= rx_data;
                            end

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
                            // Feature 11
                            // Max Packet Length
                            // 15 bits
                            // Bytes 28-29
                            // -----------------------------------------

                            6'd28: begin
                                b0 <= rx_data;
                            end

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
                            // Feature 12
                            // Total Length of Fwd Packets
                            // 21 bits
                            // Bytes 30-32
                            // -----------------------------------------

                            6'd30: begin
                                b0 <= rx_data;
                            end

                            6'd31: begin
                                b1 <= rx_data;
                            end

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
                            // Feature 13
                            // Bwd Header Length
                            // 21 bits
                            // Bytes 33-35
                            // -----------------------------------------

                            6'd33: begin
                                b0 <= rx_data;
                            end

                            6'd34: begin
                                b1 <= rx_data;
                            end

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
                            // Feature 14
                            // Flow Duration
                            // 27 bits
                            // Bytes 36-39
                            // -----------------------------------------

                            6'd36: begin
                                b0 <= rx_data;
                            end

                            6'd37: begin
                                b1 <= rx_data;
                            end

                            6'd38: begin
                                b2 <= rx_data;
                            end

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
                            // Feature 15
                            // Fwd Header Length
                            // 21 bits
                            // Bytes 40-42
                            // -----------------------------------------

                            6'd40: begin
                                b0 <= rx_data;
                            end

                            6'd41: begin
                                b1 <= rx_data;
                            end

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
                                // Should never occur.
                            end

                        endcase


                        // ------------------------------------------------
                        // Byte 42 is the final payload byte.
                        // Next received byte must be the footer 0x55.
                        // ------------------------------------------------

                        if (byte_count == 6'd42) begin

                            state <= S_FOOTER;

                        end
                        else begin

                            byte_count <= byte_count + 6'd1;

                        end

                    end


                    // =================================================
                    // WAIT FOR FOOTER
                    // =================================================

                    S_FOOTER: begin

                        if (rx_data == FOOTER) begin

                            packet_done <= 1'b1;

                        end
                        else begin

                            packet_error <= 1'b1;

                        end

                        state      <= S_IDLE;
                        byte_count <= 6'd0;

                    end


                    // =================================================
                    // DEFAULT
                    // =================================================

                    default: begin

                        state      <= S_IDLE;
                        byte_count <= 6'd0;

                    end

                endcase

            end

        end

    end

endmodule