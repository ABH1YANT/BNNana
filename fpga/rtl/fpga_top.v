`timescale 1ns / 1ps

module fpga_top #(
    parameter CLK_FREQ  = 100_000_000,
    parameter BAUD_RATE = 2_000_000
)(
    input wire clk,
    input wire rst,
    input wire uart_rx_pin,
    output wire uart_tx_pin
);

    // ============================================================
    // INTERNAL WIRE & SIGNAL DECLARATIONS
    // ============================================================

    // Clock and Reset
    wire        rst_sys;
    wire clk_sys;
    wire rst_active;

    // UART RX
    wire [7:0]  rx_data;
    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire        rx_valid;
    wire        rx_busy;

    // Packet Parser
    wire [3:0]  feature_index;
    wire [26:0] feature_in;
    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire        feature_valid;
    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire        packet_done;
    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire        packet_error;

    // Feature Register
    // ============================================================
    // DUAL-BANK FEATURE STORAGE
    // ============================================================

    wire [277:0] features;

    wire [1:0] bank_available;

    wire write_bank;
    wire completed_bank;
    wire bank_complete;

    wire bank_release;
    wire released_bank;

    reg [1:0] bank_owned;
    reg [1:0] bank_ready;

    reg read_bank;
    reg active_bank;

    // A bank is available only when it is not owned.
    assign bank_available = ~bank_owned;

    // Preprocessing
    wire [127:0] preprocessed;
    wire preprocessing_done;
    reg preprocessing_start;

    // ============================================================
    // PACKET BANK SCHEDULER
    // ============================================================

    localparam SCH_IDLE = 1'b0;
    localparam SCH_WAIT_PREP = 1'b1;

    reg scheduler_state;

    // Inference Core
    // ============================================================
    // INFERENCE CORE
    // ============================================================

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire inference_start;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire inference_busy;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire inference_done;

    wire classification;


    // ============================================================
    // DEBUG: INFERENCE CYCLE COUNTERS
    // ============================================================

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire [2:0] debug_stage;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire [31:0] input_layer_cycles;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire [31:0] hidden_layer_1_cycles;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire [31:0] hidden_layer_2_cycles;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire [31:0] output_layer_cycles;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire [31:0] inference_cycle_count;

    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire [31:0] total_inference_cycles;

    wire        result_valid;

    // UART Controller & TX
    wire [7:0]  tx_data;
    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire        tx_start;
    (* MARK_DEBUG = "TRUE", KEEP = "TRUE" *)
    wire        tx_busy;
    wire        tx_done;
    wire        uart_controller_busy;

    // ============================================================
    // BANK OWNERSHIP AND INFERENCE SCHEDULER
    // ============================================================

    always @(posedge clk_sys) begin

        if (rst_sys) begin

            bank_owned <= 2'b00;
            bank_ready <= 2'b00;

            read_bank <= 1'b0;
            active_bank <= 1'b0;

            scheduler_state <= SCH_IDLE;
            preprocessing_start <= 1'b0;

        end

        else begin

            // Default: preprocessing start is a one-cycle pulse.
            preprocessing_start <= 1'b0;


            // ----------------------------------------------------
            // BANK OWNERSHIP
            // ----------------------------------------------------

            if (feature_valid)
                bank_owned[write_bank] <= 1'b1;

            if (bank_complete) begin
                bank_owned[completed_bank] <= 1'b1;
                bank_ready[completed_bank] <= 1'b1;
            end

            if (bank_release) begin
                bank_owned[released_bank] <= 1'b0;
                bank_ready[released_bank] <= 1'b0;
            end


            // ----------------------------------------------------
            // PACKET SCHEDULER
            // ----------------------------------------------------

            case (scheduler_state)

                // -----------------------------------------------
                // SELECT A COMPLETED PACKET
                // -----------------------------------------------

                SCH_IDLE: begin

                    if (bank_ready[0]) begin

                        read_bank <= 1'b0;
                        active_bank <= 1'b0;

                        bank_ready[0] <= 1'b0;

                        preprocessing_start <= 1'b1;
                        scheduler_state <= SCH_WAIT_PREP;

                    end

                    else if (bank_ready[1]) begin

                        read_bank <= 1'b1;
                        active_bank <= 1'b1;

                        bank_ready[1] <= 1'b0;

                        preprocessing_start <= 1'b1;
                        scheduler_state <= SCH_WAIT_PREP;

                    end

                end


                // -----------------------------------------------
                // WAIT FOR PREPROCESSING COMPLETION
                // -----------------------------------------------

                SCH_WAIT_PREP: begin

                    if (preprocessing_done) begin

                        // Preprocessing has captured the complete
                        // feature vector. The bank can be reused.
                        bank_owned[active_bank] <= 1'b0;
                        bank_ready[active_bank] <= 1'b0;

                        scheduler_state <= SCH_IDLE;

                    end

                end


                default: begin
                    scheduler_state <= SCH_IDLE;
                end

            endcase

        end

    end

    // ============================================================
    // SYSTEM CLOCK AND RESET
    // ============================================================

    // Use the board's 100 MHz clock directly.
    assign clk_sys = clk;

    // Board reset is active-low.
    assign rst_active = ~rst;

    // Reset the design while the reset button is pressed.
    assign rst_sys = rst_active;


    // ============================================================
    // UART RX
    // ============================================================

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

    packet_parser packet_parser_inst (
        .clk            (clk_sys),
        .rst            (rst_sys),

        .rx_data        (rx_data),
        .rx_valid       (rx_valid),

        .feature_index  (feature_index),
        .feature_in     (feature_in),
        .feature_valid  (feature_valid),

        // Dual-bank control
        .bank_available (bank_available),
        .write_bank     (write_bank),

        .completed_bank (completed_bank),
        .bank_complete  (bank_complete),

        .bank_release   (bank_release),
        .released_bank  (released_bank),

        // Packet status
        .packet_done    (packet_done),
        .packet_error   (packet_error)
    );


    // ============================================================
    // FEATURE REGISTER
    // ============================================================

    feature_register feature_register_inst (
        .clk           (clk_sys),
        .rst           (rst_sys),

        .load          (feature_valid),

        .feature_index (feature_index),
        .feature_in    (feature_in),

        // Select parser's write bank.
        .write_bank    (write_bank),

        // Select scheduler's inference bank.
        .read_bank     (read_bank),

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

    preprocessing preprocessing_inst (
        .clk          (clk_sys),
        .rst          (rst_sys),
        .start        (preprocessing_start),
        .features     (features),
        .preprocessed (preprocessed),
        .done         (preprocessing_done)
    );

    assign inference_start = preprocessing_done;
    assign result_valid = inference_done;

    // ============================================================
    // INFERENCE CORE
    // ============================================================

    inference_core inference_core_inst (
        .clk                     (clk_sys),
        .rst                     (rst_sys),
        .start                   (inference_start),
        .features                (preprocessed),

        .classification          (classification),
        .inference_done          (inference_done),
        .busy                    (inference_busy),

        // Debug outputs
        .debug_stage             (debug_stage),
        .input_layer_cycles      (input_layer_cycles),
        .hidden_layer_1_cycles   (hidden_layer_1_cycles),
        .hidden_layer_2_cycles   (hidden_layer_2_cycles),
        .output_layer_cycles     (output_layer_cycles),
        .inference_cycle_count   (inference_cycle_count),
        .total_inference_cycles  (total_inference_cycles)
    );


    // ============================================================
    // UART CONTROLLER
    // ============================================================

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