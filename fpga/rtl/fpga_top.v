`timescale 1ns / 1ps

module fpga_top #(
    parameter CLK_FREQ  = 75_000_000,
    parameter BAUD_RATE = 115200
)(
    input wire clk,
    input wire rst,
    input wire uart_rx_pin,
    output wire uart_tx_pin
);

    // ============================================================
    // CLOCK WIZARD
    //
    // Board input clock:
    //     100 MHz
    //
    // Generated system clock:
    //     75 MHz
    // ============================================================

    wire clk_sys;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire clk_locked;

    clk_wiz_0 clk_wiz_inst (
        .clk_in1  (clk),
        .reset    (rst),
        .clk_out1 (clk_sys),
        .locked   (clk_locked)
    );


    // ============================================================
    // SYSTEM RESET
    //
    // The system remains in reset until:
    //     rst = 0
    //     clk_locked = 1
    // ============================================================

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire rst_sys;

    assign rst_sys = rst | ~clk_locked;


    // ============================================================
    // UART RX
    // ============================================================

    wire [7:0] rx_data;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire rx_valid;

    wire rx_busy;

    uart_rx #(
        .CLK_FREQ  (CLK_FREQ),
        .BAUD_RATE (BAUD_RATE)
    ) uart_rx_inst (
        .clk      (clk_sys),
        .rst      (rst_sys),
        .rx       (uart_rx_pin),
        .rx_data  (rx_data),
        .rx_valid (rx_valid),
        .busy     (rx_busy)
    );


    // ============================================================
    // PACKET PARSER
    // ============================================================

    wire [3:0]  feature_index;
    wire [26:0] feature_in;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire feature_valid;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire packet_done;

    wire packet_error;

    packet_parser packet_parser_inst (
        .clk           (clk_sys),
        .rst           (rst_sys),
        .rx_data       (rx_data),
        .rx_valid      (rx_valid),
        .feature_index (feature_index),
        .feature_in    (feature_in),
        .feature_valid (feature_valid),
        .packet_done   (packet_done),
        .packet_error  (packet_error)
    );


    // ============================================================
    // FEATURE REGISTER
    // ============================================================

    wire [277:0] features;

    feature_register feature_register_inst (
        .clk           (clk_sys),
        .rst           (rst_sys),
        .load          (feature_valid),
        .feature_index (feature_index),
        .feature_in    (feature_in),
        .features      (features)
    );


    // ============================================================
    // PREPROCESSING
    //
    // BRAM LUTs
    //     ↓
    // q0..q15 registers
    //     ↓
    // preprocessed
    // ============================================================

    wire [127:0] preprocessed;

    preprocessing preprocessing_inst (
        .clk          (clk_sys),
        .features     (features),
        .preprocessed (preprocessed)
    );


    // ============================================================
    // INFERENCE CORE
    // ============================================================

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire inference_start;

    wire inference_busy;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire inference_done;

    wire classification;

    inference_core inference_core_inst (
        .clk             (clk_sys),
        .rst             (rst_sys),
        .start           (inference_start),
        .features        (preprocessed),
        .classification  (classification),
        .inference_done  (inference_done),
        .busy            (inference_busy)
    );


    // ============================================================
    // CONTROLLER FSM
    // ============================================================

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire result_valid;

    // IMPORTANT:
    // This is separate from inference_busy.
    // controller_fsm and inference_core each drive their own
    // busy output.

    wire controller_busy;

    controller_fsm controller_fsm_inst (
        .clk             (clk_sys),
        .rst             (rst_sys),
        .start           (packet_done),
        .inference_done  (inference_done),
        .inference_start (inference_start),
        .busy            (controller_busy),
        .result_valid    (result_valid)
    );


    // ============================================================
    // UART CONTROLLER
    // ============================================================

    wire [7:0] tx_data;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire tx_start;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire tx_busy;

    wire tx_done;

    wire uart_controller_busy;

    uart_controller uart_controller_inst (
        .clk             (clk_sys),
        .rst             (rst_sys),
        .result_valid    (result_valid),
        .classification  (classification),
        .tx_data         (tx_data),
        .tx_start        (tx_start),
        .tx_busy         (tx_busy),
        .tx_done         (tx_done),
        .busy            (uart_controller_busy)
    );


    // ============================================================
    // UART TX
    // ============================================================

    uart_tx #(
        .CLK_FREQ  (CLK_FREQ),
        .BAUD_RATE (BAUD_RATE)
    ) uart_tx_inst (
        .clk      (clk_sys),
        .rst      (rst_sys),
        .tx_data  (tx_data),
        .tx_start (tx_start),
        .tx       (uart_tx_pin),
        .busy     (tx_busy),
        .tx_done  (tx_done)
    );

endmodule