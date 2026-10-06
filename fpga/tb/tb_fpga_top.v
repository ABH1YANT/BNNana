`timescale 1ns / 1ps

module tb_fpga_top;

    // ============================================================
    // CLOCK / RESET
    // ============================================================

    localparam CLK_FREQ    = 75_000_000;
    localparam BAUD_RATE   = 115200;
    localparam CLKS_PER_BIT = 651;

    reg clk;
    reg rst;

    initial begin
        clk = 1'b0;
        forever #6.666666 clk = ~clk;
    end

    // ============================================================
    // UART PINS
    // ============================================================

    reg  uart_rx_pin;
    wire uart_tx_pin;

    // ============================================================
    // UART RX
    // ============================================================

    wire [7:0] rx_data;
    wire       rx_valid;
    wire       rx_busy;

    uart_rx #(
        .CLK_FREQ  (CLK_FREQ),
        .BAUD_RATE (BAUD_RATE)
    ) uart_rx_inst (
        .clk      (clk),
        .rst      (rst),
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
    wire        feature_valid;
    wire        packet_done;
    wire        packet_error;

    packet_parser packet_parser_inst (
        .clk           (clk),
        .rst           (rst),
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
        .clk           (clk),
        .rst           (rst),
        .load          (feature_valid),
        .feature_index (feature_index),
        .feature_in    (feature_in),
        .features      (features)
    );

    // ============================================================
    // PREPROCESSING
    // ============================================================

    wire [127:0] preprocessed;

    preprocessing preprocessing_inst (
        .clk          (clk),
        .features     (features),
        .preprocessed (preprocessed)
    );

    // ============================================================
    // CONTROLLER
    // ============================================================

    wire inference_start;
    wire inference_busy;
    wire inference_done;
    wire classification;

    wire controller_busy;
    wire result_valid;

    // ============================================================
    // INFERENCE CORE
    // ============================================================

    inference_core inference_core_inst (
        .clk            (clk),
        .rst            (rst),
        .start          (inference_start),
        .features       (preprocessed),
        .classification (classification),
        .inference_done (inference_done),
        .busy           (inference_busy)
    );

    // ============================================================
    // CONTROLLER FSM
    // ============================================================

    controller_fsm controller_fsm_inst (
        .clk             (clk),
        .rst             (rst),
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
    wire       tx_start;
    wire       tx_busy;
    wire       tx_done;
    wire       uart_controller_busy;

    uart_controller uart_controller_inst (
        .clk            (clk),
        .rst            (rst),
        .result_valid   (result_valid),
        .classification(classification),
        .tx_data        (tx_data),
        .tx_start       (tx_start),
        .tx_busy        (tx_busy),
        .tx_done        (tx_done),
        .busy           (uart_controller_busy)
    );

    // ============================================================
    // UART TX
    // ============================================================

    uart_tx #(
        .CLK_FREQ  (CLK_FREQ),
        .BAUD_RATE (BAUD_RATE)
    ) uart_tx_inst (
        .clk      (clk),
        .rst      (rst),
        .tx_data  (tx_data),
        .tx_start (tx_start),
        .tx       (uart_tx_pin),
        .busy     (tx_busy),
        .tx_done  (tx_done)
    );


    // ============================================================
    // RESET
    // ============================================================

    initial begin
        rst         = 1'b1;
        uart_rx_pin = 1'b1;

        repeat (20) @(posedge clk);

        rst = 1'b0;

        $display("");
        $display("============================================================");
        $display(" BNNANA RTL SIMULATION START");
        $display("============================================================");
        $display("");

        repeat (20) @(posedge clk);

        send_packet;

        // Give the complete BNN chain time to finish.
        repeat (100000) @(posedge clk);

        $display("");
        $display("============================================================");
        $display(" SIMULATION TIMEOUT - NO UART RESULT RECEIVED");
        $display("============================================================");
        $display("");

        $finish;
    end


    // ============================================================
    // UART BYTE TRANSMITTER
    //
    // 8-N-1
    // LSB first
    // ============================================================

    task send_uart_byte;
        input [7:0] data;
        integer i;

        begin

            // START BIT
            uart_rx_pin = 1'b0;

            repeat (CLKS_PER_BIT)
                @(posedge clk);

            // DATA BITS
            for (i = 0; i < 8; i = i + 1) begin

                uart_rx_pin = data[i];

                repeat (CLKS_PER_BIT)
                    @(posedge clk);

            end

            // STOP BIT
            uart_rx_pin = 1'b1;

            repeat (CLKS_PER_BIT)
                @(posedge clk);

            $display(
                "[TB UART TX] byte = %02h",
                data
            );

        end
    endtask


    // ============================================================
    // SEND ONE FEATURE
    //
    // Little endian byte order.
    // ============================================================

    task send_feature;
        input [26:0] value;
        input integer width;

        integer i;
        integer byte_count;

        begin

            byte_count = (width + 7) / 8;

            for (i = 0; i < byte_count; i = i + 1) begin

                send_uart_byte(
                    value[i*8 +: 8]
                );

            end

        end
    endtask


    // ============================================================
    // TEST PACKET
    //
    // These are deterministic test values.
    //
    // They are NOT being claimed to be a real dataset row.
    // Their purpose is to exercise every field width.
    // ============================================================

    task send_packet;

        begin

            $display("");
            $display("------------------------------------------------------------");
            $display("[TB] Sending packet");
            $display("------------------------------------------------------------");

            // HEADER
            send_uart_byte(8'hAA);

            // ----------------------------------------------------
            // Feature 0
            // Bwd Packet Length Max
            // 14 bits
            // ----------------------------------------------------

            $display("[TB] F0  = 1234");
            send_feature(27'd1234, 14);

            // ----------------------------------------------------
            // Feature 1
            // Min Packet Length
            // 11 bits
            // ----------------------------------------------------

            $display("[TB] F1  = 321");
            send_feature(27'd321, 11);

            // ----------------------------------------------------
            // Feature 2
            // Subflow Bwd Bytes
            // 25 bits
            // ----------------------------------------------------

            $display("[TB] F2  = 54321");
            send_feature(27'd54321, 25);

            // ----------------------------------------------------
            // Feature 3
            // Total Length of Bwd Packets
            // 25 bits
            // ----------------------------------------------------

            $display("[TB] F3  = 65432");
            send_feature(27'd65432, 25);

            // ----------------------------------------------------
            // Feature 4
            // Destination Port
            // 16 bits
            // ----------------------------------------------------

            $display("[TB] F4  = 443");
            send_feature(27'd443, 16);

            // ----------------------------------------------------
            // Feature 5
            // min_seg_size_forward
            // 11 bits
            // ----------------------------------------------------

            $display("[TB] F5  = 128");
            send_feature(27'd128, 11);

            // ----------------------------------------------------
            // Feature 6
            // ACK Flag Count
            // 1 bit
            // ----------------------------------------------------

            $display("[TB] F6  = 1");
            send_feature(27'd1, 1);

            // ----------------------------------------------------
            // Feature 7
            // Subflow Bwd Packets
            // 17 bits
            // ----------------------------------------------------

            $display("[TB] F7  = 12345");
            send_feature(27'd12345, 17);

            // ----------------------------------------------------
            // Feature 8
            // Fwd Packet Length Max
            // 15 bits
            // ----------------------------------------------------

            $display("[TB] F8  = 2047");
            send_feature(27'd2047, 15);

            // ----------------------------------------------------
            // Feature 9
            // Total Backward Packets
            // 17 bits
            // ----------------------------------------------------

            $display("[TB] F9  = 22222");
            send_feature(27'd22222, 17);

            // ----------------------------------------------------
            // Feature 10
            // Subflow Fwd Bytes
            // 21 bits
            // ----------------------------------------------------

            $display("[TB] F10 = 333333");
            send_feature(27'd333333, 21);

            // ----------------------------------------------------
            // Feature 11
            // Max Packet Length
            // 15 bits
            // ----------------------------------------------------

            $display("[TB] F11 = 4095");
            send_feature(27'd4095, 15);

            // ----------------------------------------------------
            // Feature 12
            // Total Length of Fwd Packets
            // 21 bits
            // ----------------------------------------------------

            $display("[TB] F12 = 444444");
            send_feature(27'd444444, 21);

            // ----------------------------------------------------
            // Feature 13
            // Bwd Header Length
            // 21 bits
            // ----------------------------------------------------

            $display("[TB] F13 = 55555");
            send_feature(27'd55555, 21);

            // ----------------------------------------------------
            // Feature 14
            // Flow Duration
            // 27 bits
            // ----------------------------------------------------

            $display("[TB] F14 = 12345678");
            send_feature(27'd12345678, 27);

            // ----------------------------------------------------
            // Feature 15
            // Fwd Header Length
            // 21 bits
            // ----------------------------------------------------

            $display("[TB] F15 = 66666");
            send_feature(27'd66666, 21);

            // FOOTER
            send_uart_byte(8'h55);

            $display("");
            $display("[TB] Complete 45-byte packet transmitted");
            $display("");

        end

    endtask


    // ============================================================
    // RECEIVE UART RESULT
    //
    // This watches the actual uart_tx output.
    //
    // Expected:
    //
    // 00 = benign
    // 01 = DDoS
    // ============================================================

    reg [7:0] received_result;
    integer rx_bit;

    initial begin

        wait (rst == 1'b0);

        // Wait until the FPGA actually begins transmitting.
        @(negedge uart_tx_pin);

        $display("");
        $display("------------------------------------------------------------");
        $display("[TB UART RX] FPGA transmission detected");
        $display("------------------------------------------------------------");

        // We are now at the beginning of the START bit.
        //
        // Wait half a bit so we are in the center of the start bit.

        repeat (CLKS_PER_BIT / 2)
            @(posedge clk);

        if (uart_tx_pin !== 1'b0) begin

            $display(
                "[ERROR] UART start bit invalid: %b",
                uart_tx_pin
            );

            $finish;

        end

        // Move to center of first data bit.
        repeat (CLKS_PER_BIT)
            @(posedge clk);

        received_result = 8'd0;

        for (rx_bit = 0; rx_bit < 8; rx_bit = rx_bit + 1) begin

            received_result[rx_bit] = uart_tx_pin;

            repeat (CLKS_PER_BIT)
                @(posedge clk);

        end

        // Stop bit
        if (uart_tx_pin !== 1'b1) begin

            $display(
                "[ERROR] UART stop bit invalid: %b",
                uart_tx_pin
            );

        end

        $display("");
        $display("============================================================");
        $display(" FPGA UART RESULT = 0x%02h", received_result);
        $display("============================================================");

        if (received_result == 8'h00) begin

            $display("[RESULT] BENIGN");

        end
        else if (received_result == 8'h01) begin

            $display("[RESULT] DDOS");

        end
        else begin

            $display(
                "[RESULT] ERROR - unexpected value 0x%02h",
                received_result
            );

        end

        $display("");

        #1000;

        $finish;

    end


    // ============================================================
    // UART RX DEBUG
    // ============================================================

    always @(posedge clk) begin

        if (rx_valid) begin

            $display(
                "[UART RX] received byte = 0x%02h",
                rx_data
            );

        end

    end


    // ============================================================
    // PACKET PARSER DEBUG
    // ============================================================

    always @(posedge clk) begin

        if (feature_valid) begin

            $display(
                "[PARSER] Feature %0d = %0d (0x%07h)",
                feature_index,
                feature_in,
                feature_in
            );

        end

        if (packet_done) begin

            $display("");
            $display(
                "[PARSER] PACKET DONE"
            );
            $display("");

        end

        if (packet_error) begin

            $display("");
            $display(
                "[PARSER] *** PACKET ERROR ***"
            );
            $display("");

        end

    end


    // ============================================================
    // FEATURE REGISTER DEBUG
    // ============================================================

    reg [277:0] previous_features;

    initial begin
        previous_features = 278'd0;
    end

    always @(posedge clk) begin

        if (features !== previous_features) begin

            $display("");
            $display(
                "[FEATURE REGISTER] features = %071h",
                features
            );

            previous_features <= features;

        end

    end


    // ============================================================
    // PREPROCESSING DEBUG
    // ============================================================

    reg [127:0] previous_preprocessed;

    initial begin
        previous_preprocessed = 128'd0;
    end

    always @(posedge clk) begin

        if (preprocessed !== previous_preprocessed) begin

            $display("");
            $display(
                "[PREPROCESSING] preprocessed = %032h",
                preprocessed
            );

            $display(
                "[PREPROCESSING] q0  = %02h",
                preprocessing_inst.q0
            );

            $display(
                "[PREPROCESSING] q1  = %02h",
                preprocessing_inst.q1
            );

            $display(
                "[PREPROCESSING] q2  = %02h",
                preprocessing_inst.q2
            );

            $display(
                "[PREPROCESSING] q3  = %02h",
                preprocessing_inst.q3
            );

            $display(
                "[PREPROCESSING] q4  = %02h",
                preprocessing_inst.q4
            );

            $display(
                "[PREPROCESSING] q5  = %02h",
                preprocessing_inst.q5
            );

            $display(
                "[PREPROCESSING] q6  = %02h",
                preprocessing_inst.q6
            );

            $display(
                "[PREPROCESSING] q7  = %02h",
                preprocessing_inst.q7
            );

            $display(
                "[PREPROCESSING] q8  = %02h",
                preprocessing_inst.q8
            );

            $display(
                "[PREPROCESSING] q9  = %02h",
                preprocessing_inst.q9
            );

            $display(
                "[PREPROCESSING] q10 = %02h",
                preprocessing_inst.q10
            );

            $display(
                "[PREPROCESSING] q11 = %02h",
                preprocessing_inst.q11
            );

            $display(
                "[PREPROCESSING] q12 = %02h",
                preprocessing_inst.q12
            );

            $display(
                "[PREPROCESSING] q13 = %02h",
                preprocessing_inst.q13
            );

            $display(
                "[PREPROCESSING] q14 = %02h",
                preprocessing_inst.q14
            );

            $display(
                "[PREPROCESSING] q15 = %02h",
                preprocessing_inst.q15
            );

            previous_preprocessed <= preprocessed;

        end

    end


    // ============================================================
    // CONTROLLER DEBUG
    // ============================================================

    reg previous_inference_start;
    reg previous_inference_done;
    reg previous_result_valid;

    initial begin
        previous_inference_start = 1'b0;
        previous_inference_done  = 1'b0;
        previous_result_valid    = 1'b0;
    end

    always @(posedge clk) begin

        if (inference_start && !previous_inference_start) begin

            $display("");
            $display(
                "[CONTROLLER] INFERENCE START"
            );

        end

        // Detect if inference_start stays high.
        if (inference_start && previous_inference_start) begin

            $display(
                "[WARNING] inference_start is STILL HIGH"
            );

        end

        if (inference_done && !previous_inference_done) begin

            $display("");
            $display(
                "[INFERENCE] DONE"
            );

            $display(
                "[INFERENCE] classification = %b",
                classification
            );

            $display("");

        end

        if (result_valid && !previous_result_valid) begin

            $display("");
            $display(
                "[CONTROLLER] RESULT VALID"
            );

            $display(
                "[CONTROLLER] classification = %b",
                classification
            );

            $display("");

        end

        previous_inference_start <= inference_start;
        previous_inference_done  <= inference_done;
        previous_result_valid    <= result_valid;

    end


    // ============================================================
    // INFERENCE INTERNAL DEBUG
    // ============================================================

    reg [2:0] previous_stage;

    initial begin
        previous_stage = 3'd0;
    end

    always @(posedge clk) begin

        if (inference_core_inst.stage !== previous_stage) begin

            case (inference_core_inst.stage)

                3'd0:
                    $display("[INFERENCE] STAGE = IDLE");

                3'd1: begin
                    $display("[INFERENCE] STAGE = LAYER 0");

                    $display(
                        "[INFERENCE] preprocessed = %032h",
                        inference_core_inst.preprocessed_reg
                    );
                end

                3'd2: begin
                    $display("[INFERENCE] STAGE = LAYER 1");

                    $display(
                        "[INFERENCE] layer0 = %016h",
                        inference_core_inst.layer0_reg
                    );
                end

                3'd3: begin
                    $display("[INFERENCE] STAGE = LAYER 2");

                    $display(
                        "[INFERENCE] layer1 = %016h",
                        inference_core_inst.layer1_reg
                    );
                end

                3'd4: begin
                    $display("[INFERENCE] STAGE = OUTPUT");

                    $display(
                        "[INFERENCE] layer2 = %08h",
                        inference_core_inst.layer2_reg
                    );
                end

                default:
                    $display(
                        "[INFERENCE] STAGE = UNKNOWN"
                    );

            endcase

            previous_stage <= inference_core_inst.stage;

        end

    end


    // ============================================================
    // UART CONTROLLER DEBUG
    // ============================================================

    always @(posedge clk) begin

        if (tx_start) begin

            $display("");
            $display(
                "[UART CONTROLLER] TX START, data = 0x%02h",
                tx_data
            );

        end

        if (tx_done) begin

            $display(
                "[UART CONTROLLER] TX DONE"
            );

        end

    end


endmodule