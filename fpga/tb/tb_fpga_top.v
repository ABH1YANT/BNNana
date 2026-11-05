`timescale 1ns / 1ps

module tb_fpga_top;

    // ============================================================
    // CONFIGURATION
    // ============================================================

    localparam CLK_FREQ  = 100_000_000;
    localparam BAUD_RATE = 2_000_000;

    localparam real BIT_PERIOD = 1.0e9 / BAUD_RATE;

    // ============================================================
    // DUT PROBING / INTERNAL WIRES
    // ============================================================

    reg  clk;
    reg  rst;
    reg  uart_rx_drive;

    wire uart_rx_pin;
    wire uart_tx_pin;

    assign uart_rx_pin = uart_rx_drive;
    // ============================================================
    // DUT: TOP-LEVEL INSTANTIATION ONLY
    //
    // All internal design modules are instantiated by fpga_top.
    // ============================================================

    fpga_top #(
        .CLK_FREQ  (CLK_FREQ),
        .BAUD_RATE (BAUD_RATE)
    ) dut (
        // Primary I/O
        .clk                  (clk),
        .rst                  (rst),
        .uart_rx_pin          (uart_rx_pin),
        .uart_tx_pin          (uart_tx_pin)
    );

    // ============================================================
    // TEST STATUS
    // ============================================================

    integer byte_count;
    integer feature_count;
    integer results_received;
    integer pass_count;
    integer fail_count;

    integer sample_number;
    integer rx_bit;

    reg [7:0] received_result;
    reg [7:0] expected_result;

    // ============================================================
    // 100 MHz BOARD CLOCK
    // ============================================================

    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end

    // ============================================================
    // INITIALIZATION
    // ============================================================

    initial begin

        // Force all %t timestamps to display in nanoseconds.
        $timeformat(-9, 3, " ns", 12);

        rst              = 1'b0;
        uart_rx_drive    = 1'b1;

        byte_count       = 0;
        feature_count    = 0;
        results_received = 0;
        pass_count       = 0;
        fail_count       = 0;

        received_result  = 8'h00;
        expected_result  = 8'h00;

        $display("");
        $display("======================================================");
        $display(" BNNANA FPGA FULL-SYSTEM INTEGRATION TEST");
        $display("======================================================");
        $display("Board clock : 100 MHz");
        $display("System clock: 100 MHz");
        $display("UART baud   : 2000000");
        $display("Samples     : 4");
        $display("======================================================");
        $display("");

        #200;
        rst = 1'b1;

        $display("[TB] External reset released.");

        // Wait for the direct 100 MHz system clock reset to release.
        wait (rst === 1'b1);

        $display("[TB] Direct 100 MHz system clock active.");
        $display("[TB] System reset released.");

        repeat (20) @(posedge clk);

        // --------------------------------------------------------
        // SAMPLE 1
        // --------------------------------------------------------

        sample_number = 1;
        send_sample(1);

        wait (results_received >= 1);

        repeat (20) @(posedge clk);

        // --------------------------------------------------------
        // SAMPLE 2
        // --------------------------------------------------------

        sample_number = 2;
        send_sample(2);

        wait (results_received >= 2);

        repeat (20) @(posedge clk);

        // --------------------------------------------------------
        // SAMPLE 3
        // --------------------------------------------------------

        sample_number = 3;
        send_sample(3);

        wait (results_received >= 3);

        repeat (20) @(posedge clk);

        // --------------------------------------------------------
        // SAMPLE 4
        // --------------------------------------------------------

        sample_number = 4;
        send_sample(4);

        wait (results_received >= 4);

        // Allow final debug messages to print.
        repeat (20) @(posedge clk);

        // --------------------------------------------------------
        // FINAL SUMMARY
        // --------------------------------------------------------

        $display("");
        $display("======================================================");
        $display(" FINAL INTEGRATION TEST SUMMARY");
        $display("======================================================");
        $display("Packets transmitted : 4");
        $display("UART results received: %0d", results_received);
        $display("Correct classifications: %0d", pass_count);
        $display("Incorrect classifications: %0d", fail_count);
        $display("Total UART bytes sent: %0d", byte_count);
        $display("======================================================");

        if ((results_received == 4) && (fail_count == 0)) begin
            $display("[PASS] ALL FOUR SAMPLES CLASSIFIED CORRECTLY.");
        end
        else begin
            $fatal(1, "[FAIL] INTEGRATION TEST FAILED.");
        end

        $display("======================================================");
        $display("");

        $finish;

    end

    // ============================================================
    // UART BYTE TRANSMITTER
    //
    // 8-N-1, LSB first.
    // The FPGA receives this through its real uart_rx_pin.
    // ============================================================

    task send_uart_byte;
        input [7:0] data;

        integer i;

        begin

            // Start bit
            uart_rx_drive = 1'b0;
            #(BIT_PERIOD);

            // Eight data bits
            for (i = 0; i < 8; i = i + 1) begin
                uart_rx_drive = data[i];
                #(BIT_PERIOD);
            end

            // Stop bit
            uart_rx_drive = 1'b1;
            #(BIT_PERIOD);

            byte_count = byte_count + 1;

            $display(
                "[HOST TX] Byte %0d = 0x%02h",
                byte_count,
                data
            );

        end
    endtask

    // ============================================================
    // FEATURE TRANSMITTER
    //
    // Little-endian byte order.
    // Sends ceil(width/8) bytes.
    // ============================================================

    task send_feature;
        input [26:0] value;
        input integer width;

        integer i;
        integer bytes_required;
        reg [7:0] next_byte;

        begin

            bytes_required = (width + 7) / 8;

            for (i = 0; i < bytes_required; i = i + 1) begin

                next_byte = (value >> (i * 8)) & 8'hFF;

                send_uart_byte(next_byte);

            end

        end
    endtask

    // ============================================================
    // SEND ONE COMPLETE SAMPLE
    //
    // Feature order:
    //
    // F0  Bwd Packet Length Max
    // F1  Min Packet Length
    // F2  Subflow Bwd Bytes
    // F3  Total Length of Bwd Packets
    // F4  Destination Port
    // F5  min_seg_size_forward
    // F6  ACK Flag Count
    // F7  Subflow Bwd Packets
    // F8  Fwd Packet Length Max
    // F9  Total Backward Packets
    // F10 Subflow Fwd Bytes
    // F11 Max Packet Length
    // F12 Total Length of Fwd Packets
    // F13 Bwd Header Length
    // F14 Flow Duration
    // F15 Fwd Header Length
    //
    // Packet:
    // 0xAA + feature bytes + 0x55
    // ============================================================

    task send_sample;
        input integer id;

        begin

            $display("");
            $display("------------------------------------------------------");
            $display(" SENDING SAMPLE %0d", id);
            $display("------------------------------------------------------");

            // Header
            send_uart_byte(8'hAA);

            case (id)

                // =================================================
                // SAMPLE 1
                //
                // CSV Label = 1
                // =================================================

                1: begin

                    send_feature(27'd0,        14); // F0
                    send_feature(27'd401,      11); // F1
                    send_feature(27'd0,        25); // F2
                    send_feature(27'd0,        25); // F3
                    send_feature(27'd14677,    16); // F4
                    send_feature(27'd20,       11); // F5
                    send_feature(27'd0,         1); // F6
                    send_feature(27'd0,        17); // F7
                    send_feature(27'd401,      15); // F8
                    send_feature(27'd0,        17); // F9
                    send_feature(27'd802,      21); // F10
                    send_feature(27'd401,      15); // F11
                    send_feature(27'd802,      21); // F12
                    send_feature(27'd0,        21); // F13
                    send_feature(27'd1,        27); // F14
                    send_feature(27'd40,       21); // F15

                end

                // =================================================
                // SAMPLE 2
                //
                // CSV Label = 0
                // =================================================

                2: begin

                    send_feature(27'd0,        14); // F0
                    send_feature(27'd0,        11); // F1
                    send_feature(27'd0,        25); // F2
                    send_feature(27'd0,        25); // F3
                    send_feature(27'd80,       16); // F4
                    send_feature(27'd32,       11); // F5
                    send_feature(27'd1,         1); // F6
                    send_feature(27'd6,        17); // F7
                    send_feature(27'd0,        15); // F8
                    send_feature(27'd6,        17); // F9
                    send_feature(27'd0,        21); // F10
                    send_feature(27'd0,        15); // F11
                    send_feature(27'd0,        21); // F12
                    send_feature(27'd192,      21); // F13
                    send_feature(27'd54171972, 27); // F14
                    send_feature(27'd224,      21); // F15

                end

                // =================================================
                // SAMPLE 3
                //
                // CSV Label = 1
                // =================================================

                3: begin

                    send_feature(27'd0,        14); // F0
                    send_feature(27'd401,      11); // F1
                    send_feature(27'd0,        25); // F2
                    send_feature(27'd0,        25); // F3
                    send_feature(27'd56952,    16); // F4
                    send_feature(27'd0,        11); // F5
                    send_feature(27'd0,         1); // F6
                    send_feature(27'd0,        17); // F7
                    send_feature(27'd401,      15); // F8
                    send_feature(27'd0,        17); // F9
                    send_feature(27'd802,      21); // F10
                    send_feature(27'd401,      15); // F11
                    send_feature(27'd802,      21); // F12
                    send_feature(27'd0,        21); // F13
                    send_feature(27'd1,        27); // F14
                    send_feature(27'd0,        21); // F15

                end

                // =================================================
                // SAMPLE 4
                //
                // CSV Label = 0
                // =================================================

                4: begin

                    send_feature(27'd55,       14); // F0
                    send_feature(27'd39,       11); // F1
                    send_feature(27'd110,      25); // F2
                    send_feature(27'd110,      25); // F3
                    send_feature(27'd53,       16); // F4
                    send_feature(27'd32,       11); // F5
                    send_feature(27'd0,         1); // F6
                    send_feature(27'd2,        17); // F7
                    send_feature(27'd39,       15); // F8
                    send_feature(27'd2,        17); // F9
                    send_feature(27'd78,       21); // F10
                    send_feature(27'd55,       15); // F11
                    send_feature(27'd78,       21); // F12
                    send_feature(27'd64,       21); // F13
                    send_feature(27'd134120,   27); // F14
                    send_feature(27'd64,       21); // F15

                end

                default: begin
                    $fatal(1, "Invalid sample ID: %0d", id);
                end

            endcase

            // Footer
            send_uart_byte(8'h55);

            $display(
                "[TB] Sample %0d packet transmitted.",
                id
            );

        end
    endtask

    // ============================================================
    // UART RESULT MONITOR
    //
    // This monitor runs concurrently with packet transmission.
    // It can therefore catch an FPGA response even if the FPGA
    // begins transmitting before send_sample() returns.
    //
    // The result is decoded from the actual output pin.
    // ============================================================

    
    initial begin

        wait (rst === 1'b0);

        forever begin

            // Detect the falling edge of the UART start bit.
            @(negedge uart_tx_pin);

            // Check the start bit at its midpoint.
            #(BIT_PERIOD / 2.0);

            if (uart_tx_pin !== 1'b0) begin

                $display("[ERROR] UART start bit invalid: %b",
                        uart_tx_pin);

                fail_count = fail_count + 1;
                results_received = results_received + 1;

            end
            else begin

                // Advance to the center of data bit 0.
                #(BIT_PERIOD);

                received_result = 8'h00;

                // Sample 8 data bits, LSB first.
                for (rx_bit = 0; rx_bit < 8; rx_bit = rx_bit + 1) begin

                    received_result[rx_bit] = uart_tx_pin;

                    #(BIT_PERIOD);

                end

                // We are now at the center of the stop bit.
                if (uart_tx_pin !== 1'b1)
                    $display("[ERROR] UART stop bit invalid.");

                // Determine expected result from sample order.
                case (results_received)
                    0: expected_result = 8'h01;
                    1: expected_result = 8'h00;
                    2: expected_result = 8'h01;
                    3: expected_result = 8'h00;
                    default: expected_result = 8'hFF;
                endcase

                $display("");
                $display("======================================================");
                $display("[UART RX] Result for sample %0d",
                        results_received + 1);
                $display("[UART RX] Received = 0x%02h", received_result);
                $display("[UART RX] Expected = 0x%02h", expected_result);

                if (received_result === expected_result) begin

                    $display("[PASS] Classification matches CSV label.");
                    pass_count = pass_count + 1;

                end
                else begin

                    $display("[FAIL] Classification differs from CSV label.");
                    fail_count = fail_count + 1;

                end

                results_received = results_received + 1;

                $display("======================================================");
                $display("");

            end

        end

    end

    // ============================================================
    // PREPROCESSING VERIFICATION AND TIMING MONITOR
    // ============================================================

    integer prep_sample_count;

    realtime prep_start_time;
    realtime prep_lookup_time;
    realtime prep_output_time;

    reg prep_active;

    reg [277:0] prep_features_snapshot;
    reg [127:0] prep_expected;

    // Independent reference copies of the preprocessing LUTs.
    reg [7:0] expected_lut_0  [0:4095];
    reg [7:0] expected_lut_1  [0:1023];
    reg [7:0] expected_lut_2  [0:65535];
    reg [7:0] expected_lut_3  [0:65535];
    reg [7:0] expected_lut_4  [0:4095];
    reg [7:0] expected_lut_5  [0:1023];
    reg [7:0] expected_lut_6  [0:1];
    reg [7:0] expected_lut_7  [0:4095];
    reg [7:0] expected_lut_8  [0:4095];
    reg [7:0] expected_lut_9  [0:4095];
    reg [7:0] expected_lut_10 [0:65535];
    reg [7:0] expected_lut_11 [0:4095];
    reg [7:0] expected_lut_12 [0:65535];
    reg [7:0] expected_lut_13 [0:65535];
    reg [7:0] expected_lut_14 [0:65535];
    reg [7:0] expected_lut_15 [0:65535];

    initial begin
        $readmemh("Bwd_Packet_Length_Max.mem",       expected_lut_0);
        $readmemh("Min_Packet_Length.mem",           expected_lut_1);
        $readmemh("Subflow_Bwd_Bytes.mem",           expected_lut_2);
        $readmemh("Total_Length_of_Bwd_Packets.mem", expected_lut_3);
        $readmemh("Destination_Port.mem",            expected_lut_4);
        $readmemh("min_seg_size_forward.mem",        expected_lut_5);
        $readmemh("ACK_Flag_Count.mem",              expected_lut_6);
        $readmemh("Subflow_Bwd_Packets.mem",         expected_lut_7);
        $readmemh("Fwd_Packet_Length_Max.mem",       expected_lut_8);
        $readmemh("Total_Backward_Packets.mem",      expected_lut_9);
        $readmemh("Subflow_Fwd_Bytes.mem",           expected_lut_10);
        $readmemh("Max_Packet_Length.mem",           expected_lut_11);
        $readmemh("Total_Length_of_Fwd_Packets.mem", expected_lut_12);
        $readmemh("Bwd_Header_Length.mem",           expected_lut_13);
        $readmemh("Flow_Duration.mem",               expected_lut_14);
        $readmemh("Fwd_Header_Length.mem",           expected_lut_15);
    end

    initial begin
        prep_sample_count = 0;
        prep_start_time = 0.0;
        prep_lookup_time = 0.0;
        prep_output_time = 0.0;
        prep_active = 1'b0;
        prep_features_snapshot = 278'd0;
        prep_expected = 128'd0;
    end

    always @(posedge clk) begin

        if (rst) begin
            prep_active = 1'b0;
        end

        else begin

            // ----------------------------------------------------
            // DETECT ACTUAL PREPROCESSING START
            // ----------------------------------------------------

            if (!prep_active && dut.preprocessing_start) begin

                prep_active = 1'b1;
                prep_sample_count = prep_sample_count + 1;

                prep_start_time = $realtime;

                // Observe values after nonblocking assignments.
                #0.001;

                prep_features_snapshot = dut.features;

                prep_expected = {
                    expected_lut_15[prep_features_snapshot[277:262]],
                    expected_lut_14[prep_features_snapshot[256:241]],
                    expected_lut_13[prep_features_snapshot[229:214]],
                    expected_lut_12[prep_features_snapshot[208:193]],
                    expected_lut_11[prep_features_snapshot[187:176]],
                    expected_lut_10[prep_features_snapshot[172:157]],
                    expected_lut_9 [prep_features_snapshot[151:140]],
                    expected_lut_8 [prep_features_snapshot[134:123]],
                    expected_lut_7 [prep_features_snapshot[119:108]],
                    expected_lut_6 [prep_features_snapshot[102]],
                    expected_lut_5 [prep_features_snapshot[101:92]],
                    expected_lut_4 [prep_features_snapshot[90:79]],
                    expected_lut_3 [prep_features_snapshot[74:59]],
                    expected_lut_2 [prep_features_snapshot[49:34]],
                    expected_lut_1 [prep_features_snapshot[24:15]],
                    expected_lut_0 [prep_features_snapshot[13:2]]
                };

                prep_lookup_time = $realtime;

                $display("");
                $display("[PREP-CHECK] Sample %0d", prep_sample_count);

                if (dut.features !== prep_features_snapshot) begin
                    $display("[PREP-FAIL] Feature bus changed.");
                    fail_count = fail_count + 1;
                end
                else begin
                    $display("[PREP-PASS] Feature bus stable.");
                end
            end

            // ----------------------------------------------------
            // CHECK REGISTERED PREPROCESSED OUTPUT
            // ----------------------------------------------------

            else if (prep_active) begin

                #0.001;

                prep_output_time = $realtime;

                if (dut.features !== prep_features_snapshot) begin
                    $display("[PREP-FAIL] Feature bus changed.");
                    fail_count = fail_count + 1;
                end

                if (dut.preprocessed !== prep_expected) begin

                    $display("[PREP-FAIL] Preprocessed register mismatch.");
                    fail_count = fail_count + 1;

                end
                else begin
                    $display("[PREP-PASS] Preprocessed register correct.");
                end

                if (dut.preprocessed !== prep_expected) begin
                    $display("[PREP-FAIL] Final preprocessing output mismatch.");
                    fail_count = fail_count + 1;
                end
                else begin
                    $display("[PREP-PASS] Final preprocessing output correct.");
                end

                $display("[PREP-CHECK] Start time  : %0.3f ns",
                         prep_start_time);

                $display("[PREP-CHECK] Lookup time : %0.3f ns",
                         prep_lookup_time);

                $display("[PREP-CHECK] Output time : %0.3f ns",
                         prep_output_time);

                $display("[PREP-CHECK] Total latency: %0.3f ns",
                         prep_output_time - prep_start_time);

                prep_active = 1'b0;

                $display("[PREP-CHECK] End of sample %0d",
                         prep_sample_count);

            end

        end
    end

    // ============================================================
    // PIPELINE CYCLE MONITOR
    // ============================================================

    always @(posedge clk) begin

        if (rst && dut.inference_done) begin

            #0.001;

            $display("");
            $display("========== INFERENCE TIMING ==========");
            $display("Input layer cycles     = %0d",
                     dut.input_layer_cycles);

            $display("Hidden layer 1 cycles  = %0d",
                     dut.hidden_layer_1_cycles);

            $display("Hidden layer 2 cycles  = %0d",
                     dut.hidden_layer_2_cycles);

            $display("Output layer cycles    = %0d",
                     dut.output_layer_cycles);

            $display("Total inference cycles = %0d",
                     dut.total_inference_cycles);

            $display("======================================");

        end

    end


    // ============================================================
    // DEBUG MONITOR
    //
    // These are hierarchical observations only. The DUT is
    // still instantiated exclusively through fpga_top.
    // ============================================================

    always @(posedge clk) begin

        if (!rst === 1'b0) begin

            if (dut.feature_valid) begin

                feature_count = feature_count + 1;

                $display(
                    "[PARSER] Index=%0d Value=%0d",
                    dut.feature_index,
                    dut.feature_in
                );

            end

            if (dut.packet_parser_inst.packet_error) begin

                $display("[ERROR] Packet parser reported an error.");

            end

            if (dut.packet_done) begin

                $display(
                    "[PARSER] Packet complete. Feature events=%0d",
                    feature_count
                );

            end

            if (dut.inference_start) begin

                $display("[CONTROLLER] Inference start.");

            end

            if (dut.inference_done) begin

                $display(
                    "[INFERENCE] Done. Classification=%b",
                    dut.classification
                );

            end

            if (dut.inference_done) begin

                $display(
                    "[CONTROLLER] Result valid. Classification=%b",
                    dut.classification
                );

            end

            if (dut.tx_start) begin

                $display(
                    "[UART TX] Start. Data=0x%02h",
                    dut.tx_data
                );

            end

        end

    end

    // ============================================================
    // GLOBAL WATCHDOG
    //
    // Four packets require approximately 900 us of UART
    // transmission time alone at 2 Mbps.
    // ============================================================

    initial begin

        #100_000_000;

        $display("");
        $display("======================================================");
        $display("[FAIL] GLOBAL SIMULATION TIMEOUT");
        $display("======================================================");
        $display("System reset       = %b", ~rst);
        $display("Packet done        = %b", dut.packet_done);
        $display("Packet error       = %b", dut.packet_error);
        $display("Inference start    = %b", dut.inference_start);
        $display("Inference busy     = %b", dut.inference_busy);
        $display("Inference done     = %b", dut.inference_done);
        $display("Classification     = %b", dut.classification);
        $display("Result valid       = %b", dut.inference_done);
        $display("UART TX busy       = %b", dut.tx_busy);
        $display("UART TX pin        = %b", uart_tx_pin);
        $display("Bytes sent         = %0d", byte_count);
        $display("Feature events     = %0d", feature_count);
        $display("Results received   = %0d", results_received);
        $display("======================================================");

        $fatal(1, "Integration test timed out.");

    end

endmodule
