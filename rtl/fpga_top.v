`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/26/2026 02:07:43 AM
// Design Name: 
// Module Name: fpga_top
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


module fpga_top #(
    parameter CLKS_PER_BIT = 868,
    parameter FEATURE_COUNT = 15,
    parameter FEATURE_WIDTH = 8,
    parameter NEURON_COUNT = 16,
    parameter ACC_WIDTH = 16
)(
    input wire clk,
    input wire rst,
    input wire rx,
    output wire tx
);

    // --- Internal Wires ---
    
    // UART <-> Parser/FSM
    wire [7:0] rx_data;
    wire rx_valid;
    wire [7:0] tx_data;
    wire tx_start;
    wire tx_busy;
    
    // Parser <-> Register/FSM
    wire [(FEATURE_COUNT * FEATURE_WIDTH)-1:0] parsed_features;
    wire packet_valid;
    
    // Register <-> Inference Core
    wire [(FEATURE_COUNT * FEATURE_WIDTH)-1:0] registered_features;
    wire load_enable;
    
    // BRAM <-> Inference Core
    wire [(NEURON_COUNT * FEATURE_COUNT)-1:0] all_weights;
    wire [(NEURON_COUNT * ACC_WIDTH)-1:0] all_thresholds;
    
    // Inference Core <-> FSM
    wire classification;

    // --- Module Instantiations ---

    uart_controller #(.CLKS_PER_BIT(CLKS_PER_BIT)) uart_inst (
        .clk(clk), .rst(rst), .rx(rx), .tx(tx),
        .rx_data(rx_data), .rx_valid(rx_valid),
        .tx_data(tx_data), .tx_start(tx_start), .tx_busy(tx_busy)
    );

    packet_parser #(.FEATURE_COUNT(FEATURE_COUNT), .START_BYTE(8'hAA)) parser_inst (
        .clk(clk), .rst(rst),
        .rx_data(rx_data), .rx_valid(rx_valid),
        .feature_vector(parsed_features), .packet_valid(packet_valid)
    );

    feature_register #(.FEATURE_COUNT(FEATURE_COUNT), .FEATURE_WIDTH(FEATURE_WIDTH)) reg_inst (
        .clk(clk), .rst(rst),
        .feature_vector(parsed_features), .load_enable(load_enable),
        .registered_features(registered_features)
    );

    weight_bram #(.NEURON_COUNT(NEURON_COUNT), .INPUT_COUNT(FEATURE_COUNT)) w_bram_inst (
        .all_weights(all_weights)
    );

    threshold_bram #(.NEURON_COUNT(NEURON_COUNT), .ACC_WIDTH(ACC_WIDTH)) t_bram_inst (
        .all_thresholds(all_thresholds)
    );

    // From Workstream C1!
    inference_core #(
        .FEATURE_COUNT(FEATURE_COUNT), .HIDDEN_NEURON_COUNT(NEURON_COUNT),
        .FEATURE_WIDTH(FEATURE_WIDTH), .ACC_WIDTH(ACC_WIDTH)
    ) ai_core_inst (
        .feature_vector(registered_features),
        .hidden_weights(all_weights),
        .hidden_thresholds(all_thresholds),
        .output_weights(16'hFFFF),     // Hardcoded output weights for now
        .output_threshold(16'sd10),    // Hardcoded output threshold for now
        .classification(classification)
    );

    controller_fsm fsm_inst (
        .clk(clk), .rst(rst),
        .packet_valid(packet_valid), .load_enable(load_enable),
        .classification(classification),
        .tx_data(tx_data), .tx_start(tx_start), .tx_busy(tx_busy)
    );

endmodule
