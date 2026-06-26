`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/24/2026 01:56:20 AM
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


module packet_parser #(
    parameter FEATURE_COUNT = 15,
    parameter START_BYTE = 8'hAA
)(
    input wire clk,
    input wire rst,
    
    // Interface from UART Controller
    input wire [7:0] rx_data,
    input wire rx_valid,
    
    // Interface to Feature Register
    output wire [(FEATURE_COUNT * 8)-1:0] feature_vector,
    output wire packet_valid
);

    // FSM States
    localparam WAIT_START       = 2'b00;
    localparam COLLECT_FEATURES = 2'b01;
    localparam WAIT_CHECKSUM    = 2'b10;

    reg [1:0] state;
    reg [3:0] byte_count; // Needs to count 0 to 14
    reg [7:0] calculated_checksum;
    
    reg [(FEATURE_COUNT * 8)-1:0] features_reg;
    reg valid_reg;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state <= WAIT_START;
            byte_count <= 0;
            calculated_checksum <= 0;
            features_reg <= 0;
            valid_reg <= 0;
        end else begin
            // Default: valid pulse is only 1 clock cycle long
            valid_reg <= 1'b0; 

            case (state)
                WAIT_START: begin
                    if (rx_valid == 1'b1) begin
                        if (rx_data == START_BYTE) begin
                            state <= COLLECT_FEATURES;
                            byte_count <= 0;
                            calculated_checksum <= 0;
                        end
                        // If it's not the start byte, we just ignore it and stay in WAIT_START
                    end
                end

                COLLECT_FEATURES: begin
                    if (rx_valid == 1'b1) begin
                        // Store the byte in the correct slice of the massive register
                        features_reg[byte_count * 8 +: 8] <= rx_data;
                        
                        // Add to running checksum (8-bit overflow is intentional and expected)
                        calculated_checksum <= calculated_checksum + rx_data;
                        
                        if (byte_count < FEATURE_COUNT - 1) begin
                            byte_count <= byte_count + 1;
                        end else begin
                            state <= WAIT_CHECKSUM;
                        end
                    end
                end

                WAIT_CHECKSUM: begin
                    if (rx_valid == 1'b1) begin
                        if (rx_data == calculated_checksum) begin
                            // Checksum matches! The packet is perfect.
                            valid_reg <= 1'b1;
                        end else begin
                            // Checksum failed! Corrupted data. Drop it silently.
                            valid_reg <= 1'b0;
                        end
                        // Regardless of pass or fail, go back to waiting for the next packet
                        state <= WAIT_START;
                    end
                end
                
                default: state <= WAIT_START;
            endcase
        end
    end

    assign feature_vector = features_reg;
    assign packet_valid = valid_reg;

endmodule
