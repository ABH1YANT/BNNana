`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/26/2026 01:57:25 AM
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


module controller_fsm (
    input wire clk,
    input wire rst,
    
    // Interface from Packet Parser
    input wire packet_valid,
    
    // Interface to Feature Register
    output wire load_enable,
    
    // Interface from Neural Network (Inference Core)
    input wire classification,
    
    // Interface to UART Transmitter
    output wire [7:0] tx_data,
    output wire tx_start,
    input wire tx_busy
);

    // FSM States
    localparam IDLE           = 3'b000;
    localparam LOAD_FEATURES  = 3'b001;
    localparam WAIT_INFERENCE = 3'b010;
    localparam SEND_RESULT    = 3'b011;
    localparam WAIT_TX        = 3'b100;

    reg [2:0] state;
    reg [1:0] wait_counter; // Counter to give the neural network time to calculate
    
    reg load_enable_reg;
    reg [7:0] tx_data_reg;
    reg tx_start_reg;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state <= IDLE;
            wait_counter <= 0;
            load_enable_reg <= 0;
            tx_data_reg <= 0;
            tx_start_reg <= 0;
        end else begin
            // Default values (pulses default to 0)
            load_enable_reg <= 1'b0;
            tx_start_reg <= 1'b0;

            case (state)
                IDLE: begin
                    if (packet_valid == 1'b1) begin
                        state <= LOAD_FEATURES;
                    end
                end

                LOAD_FEATURES: begin
                    // Pulse load_enable to freeze the features in the register
                    load_enable_reg <= 1'b1;
                    wait_counter <= 0;
                    state <= WAIT_INFERENCE;
                end

                WAIT_INFERENCE: begin
                    // Wait 3 clock cycles for the combinational logic of the 
                    // Neural Network to settle and produce a stable classification
                    if (wait_counter < 3) begin
                        wait_counter <= wait_counter + 1;
                    end else begin
                        state <= SEND_RESULT;
                    end
                end

                SEND_RESULT: begin
                    // Pad the 1-bit classification with 7 zeros to make a byte
                    tx_data_reg <= {7'b0000000, classification};
                    
                    // Pulse tx_start to wake up the UART transmitter
                    tx_start_reg <= 1'b1;
                    state <= WAIT_TX;
                end

                WAIT_TX: begin
                    // Wait until the UART transmitter finishes sending the byte
                    // (tx_busy will go high, then eventually drop to 0)
                    if (tx_busy == 1'b0 && tx_start_reg == 1'b0) begin
                        state <= IDLE; // Ready for the next packet!
                    end
                end
                
                default: state <= IDLE;
            endcase
        end
    end

    // Assign internal registers to output wires
    assign load_enable = load_enable_reg;
    assign tx_data = tx_data_reg;
    assign tx_start = tx_start_reg;

endmodule