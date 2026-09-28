`timescale 1ns / 1ps

module fpga_top #(
    parameter CLK_FREQ  = 100_000_000,
    parameter BAUD_RATE = 115200
)(
    input  wire clk,
    input  wire rst,

    input  wire uart_rx_pin,
    output wire uart_tx_pin
);

    // ============================================================
    // UART RX
    // ============================================================

    wire [7:0] rx_data;
    wire       rx_valid;
    wire       rx_busy;

    uart_rx #(
        .CLK_FREQ(CLK_FREQ),
        .BAUD_RATE(BAUD_RATE)
    ) uart_rx_inst (
        .clk(clk),
        .rst(rst),
        .rx(uart_rx_pin),
        .rx_data(rx_data),
        .rx_valid(rx_valid),
        .busy(rx_busy)
    );


    // ============================================================
    // PACKET PARSER
    // ============================================================

    wire [3:0]  feature_index;
    wire [26:0] feature_in;
    wire        feature_valid;

    wire        packet_done;
    wire        packet_error;

    packet_parser packet_parser_inst (
        .clk(clk),
        .rst(rst),
        .rx_data(rx_data),
        .rx_valid(rx_valid),

        .feature_index(feature_index),
        .feature_in(feature_in),
        .feature_valid(feature_valid),

        .packet_done(packet_done),
        .packet_error(packet_error)
    );


    // ============================================================
    // FEATURE REGISTER
    // ============================================================

    wire [277:0] features;

    feature_register feature_register_inst (
        .clk(clk),
        .rst(rst),

        .load(feature_valid),
        .feature_index(feature_index),
        .feature_in(feature_in),

        .features(features)
    );


    // ============================================================
    // PREPROCESSING
    //
    // IMPORTANT:
    // The updated preprocessing module uses synchronous BRAM.
    // Therefore it has one clock cycle of latency.
    // ============================================================

    wire [127:0] preprocessed;

    preprocessing preprocessing_inst (
        .clk(clk),
        .features(features),
        .preprocessed(preprocessed)
    );


    // ============================================================
    // CONTROLLER SIGNALS
    // ============================================================

    wire inference_start;
    wire inference_busy;
    wire result_valid;

    wire inference_done;


    // ============================================================
    // BNN INFERENCE
    //
    // The updated inference_core is pipelined:
    //
    // Layer 0
    //    ↓
    // register
    //    ↓
    // Layer 1
    //    ↓
    // register
    //    ↓
    // Layer 2
    //    ↓
    // register
    //    ↓
    // Output
    //
    // It generates the actual inference_done signal.
    // ============================================================

    wire classification;

    inference_core inference_core_inst (
        .clk(clk),
        .rst(rst),

        .start(inference_start),

        .features(preprocessed),

        .classification(classification),
        .inference_done(inference_done),
        .busy(inference_busy)
    );


    // ============================================================
    // CONTROLLER FSM
    // ============================================================

    controller_fsm controller_fsm_inst (
        .clk(clk),
        .rst(rst),

        .start(packet_done),
        .inference_done(inference_done),

        .inference_start(inference_start),
        .busy(inference_busy),
        .result_valid(result_valid)
    );


    // ============================================================
    // UART CONTROLLER
    // ============================================================

    wire [7:0] tx_data;
    wire       tx_start;
    wire       tx_busy;
    wire       tx_done;
    wire       uart_controller_busy;

    uart_controller uart_controller_inst (
        .clk(clk),
        .rst(rst),

        .result_valid(result_valid),
        .classification(classification),

        .tx_data(tx_data),
        .tx_start(tx_start),
        .tx_busy(tx_busy),
        .tx_done(tx_done),

        .busy(uart_controller_busy)
    );


    // ============================================================
    // UART TX
    // ============================================================

    uart_tx #(
        .CLK_FREQ(CLK_FREQ),
        .BAUD_RATE(BAUD_RATE)
    ) uart_tx_inst (
        .clk(clk),
        .rst(rst),

        .tx_data(tx_data),
        .tx_start(tx_start),

        .tx(uart_tx_pin),
        .busy(tx_busy),
        .tx_done(tx_done)
    );

endmodule