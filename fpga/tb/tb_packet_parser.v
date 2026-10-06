`timescale 1ns / 1ps

module packet_parser_tb;

    // ============================================================
    // DUT signals
    // ============================================================

    reg         clk;
    reg         rst;

    reg  [7:0]  rx_data;
    reg         rx_valid;

    wire [3:0]  feature_index;
    wire [26:0] feature_in;
    wire        feature_valid;

    wire        packet_done;
    wire        packet_error;


    // ============================================================
    // DUT
    // ============================================================

    packet_parser dut (
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
    // 100 MHz simulation clock
    // ============================================================

    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end


    // ============================================================
    // Test values
    //
    // Chosen values are deliberately non-zero and easy to verify.
    // ============================================================

    reg [13:0] f0;
    reg [10:0] f1;
    reg [24:0] f2;
    reg [24:0] f3;
    reg [15:0] f4;
    reg [10:0] f5;
    reg        f6;
    reg [16:0] f7;
    reg [14:0] f8;
    reg [16:0] f9;
    reg [20:0] f10;
    reg [14:0] f11;
    reg [20:0] f12;
    reg [20:0] f13;
    reg [26:0] f14;
    reg [20:0] f15;


    // ============================================================
    // Expected feature counter
    // ============================================================

    integer feature_count;
    integer errors;


    // ============================================================
    // Send one byte
    // ============================================================

    task send_byte;

        input [7:0] data;

        begin

            @(posedge clk);

            rx_data  <= data;
            rx_valid <= 1'b1;

            @(posedge clk);

            rx_valid <= 1'b0;
            rx_data  <= 8'h00;

        end

    endtask


    // ============================================================
    // Check one feature
    // ============================================================

    task check_feature;

        input [3:0]  expected_index;
        input [26:0] expected_value;

        begin

            @(posedge clk);

            if (feature_valid !== 1'b1) begin

                $display(
                    "ERROR: Expected feature_valid for feature %0d",
                    expected_index
                );

                errors = errors + 1;

            end
            else begin

                if (feature_index !== expected_index) begin

                    $display(
                        "ERROR: Feature index mismatch. Expected=%0d Got=%0d",
                        expected_index,
                        feature_index
                    );

                    errors = errors + 1;

                end

                if (feature_in !== expected_value) begin

                    $display(
                        "ERROR: Feature %0d value mismatch. Expected=%0d (0x%h) Got=%0d (0x%h)",
                        expected_index,
                        expected_value,
                        expected_value,
                        feature_in,
                        feature_in
                    );

                    errors = errors + 1;

                end

                if ((feature_index === expected_index) &&
                    (feature_in === expected_value)) begin

                    $display(
                        "PASS: Feature %0d = %0d (0x%h)",
                        expected_index,
                        feature_in,
                        feature_in
                    );

                end

            end

        end

    endtask


    // ============================================================
    // Main test
    // ============================================================

    initial begin

        // --------------------------------------------------------
        // Initialize
        // --------------------------------------------------------

        rst      = 1'b1;
        rx_data  = 8'h00;
        rx_valid = 1'b0;

        feature_count = 0;
        errors        = 0;


        // --------------------------------------------------------
        // Test feature values
        // --------------------------------------------------------

        f0  = 14'd12345;
        f1  = 11'd987;
        f2  = 25'd1234567;
        f3  = 25'd7654321;
        f4  = 16'd54321;
        f5  = 11'd1200;
        f6  = 1'b1;
        f7  = 17'd54321;
        f8  = 15'd12345;
        f9  = 17'd98765;
        f10 = 21'd654321;
        f11 = 15'd23456;
        f12 = 21'd765432;
        f13 = 21'd456789;
        f14 = 27'd98765432;
        f15 = 21'd345678;


        // --------------------------------------------------------
        // Reset
        // --------------------------------------------------------

        repeat (3)
            @(posedge clk);

        rst <= 1'b0;

        repeat (2)
            @(posedge clk);


        $display("");
        $display("============================================================");
        $display(" PACKET PARSER TEST");
        $display("============================================================");
        $display("Packet format:");
        $display("  Header  : AA");
        $display("  Payload : 43 bytes");
        $display("  Footer  : 55");
        $display("============================================================");
        $display("");


        // ========================================================
        // HEADER
        // ========================================================

        send_byte(8'hAA);


        // ========================================================
        // FEATURE 0
        // Bwd Packet Length Max
        // 14 bits
        //
        // Little endian:
        // byte0 = [7:0]
        // byte1 = [13:8]
        // ========================================================

        send_byte(f0[7:0]);
        send_byte({2'b00, f0[13:8]});

        check_feature(4'd0, {{13{1'b0}}, f0});


        // ========================================================
        // FEATURE 1
        // Min Packet Length
        // 11 bits
        // ========================================================

        send_byte(f1[7:0]);
        send_byte({5'b00000, f1[10:8]});

        check_feature(4'd1, {{16{1'b0}}, f1});


        // ========================================================
        // FEATURE 2
        // Subflow Bwd Bytes
        // 25 bits
        // ========================================================

        send_byte(f2[7:0]);
        send_byte(f2[15:8]);
        send_byte(f2[23:16]);
        send_byte({7'b0000000, f2[24]});

        check_feature(4'd2, {{2{1'b0}}, f2});


        // ========================================================
        // FEATURE 3
        // Total Length of Bwd Packets
        // 25 bits
        // ========================================================

        send_byte(f3[7:0]);
        send_byte(f3[15:8]);
        send_byte(f3[23:16]);
        send_byte({7'b0000000, f3[24]});

        check_feature(4'd3, {{2{1'b0}}, f3});


        // ========================================================
        // FEATURE 4
        // Destination Port
        // 16 bits
        // ========================================================

        send_byte(f4[7:0]);
        send_byte(f4[15:8]);

        check_feature(4'd4, {{11{1'b0}}, f4});


        // ========================================================
        // FEATURE 5
        // min_seg_size_forward
        // 11 bits
        // ========================================================

        send_byte(f5[7:0]);
        send_byte({5'b00000, f5[10:8]});

        check_feature(4'd5, {{16{1'b0}}, f5});


        // ========================================================
        // FEATURE 6
        // ACK Flag Count
        // 1 bit
        // ========================================================

        send_byte({7'b0000000, f6});

        check_feature(4'd6, {{26{1'b0}}, f6});


        // ========================================================
        // FEATURE 7
        // Subflow Bwd Packets
        // 17 bits
        // ========================================================

        send_byte(f7[7:0]);
        send_byte(f7[15:8]);
        send_byte({7'b0000000, f7[16]});

        check_feature(4'd7, {{10{1'b0}}, f7});


        // ========================================================
        // FEATURE 8
        // Fwd Packet Length Max
        // 15 bits
        // ========================================================

        send_byte(f8[7:0]);
        send_byte({1'b0, f8[14:8]});

        check_feature(4'd8, {{12{1'b0}}, f8});


        // ========================================================
        // FEATURE 9
        // Total Backward Packets
        // 17 bits
        // ========================================================

        send_byte(f9[7:0]);
        send_byte(f9[15:8]);
        send_byte({7'b0000000, f9[16]});

        check_feature(4'd9, {{10{1'b0}}, f9});


        // ========================================================
        // FEATURE 10
        // Subflow Fwd Bytes
        // 21 bits
        // ========================================================

        send_byte(f10[7:0]);
        send_byte(f10[15:8]);
        send_byte({3'b000, f10[20:16]});

        check_feature(4'd10, {{6{1'b0}}, f10});


        // ========================================================
        // FEATURE 11
        // Max Packet Length
        // 15 bits
        // ========================================================

        send_byte(f11[7:0]);
        send_byte({1'b0, f11[14:8]});

        check_feature(4'd11, {{12{1'b0}}, f11});


        // ========================================================
        // FEATURE 12
        // Total Length of Fwd Packets
        // 21 bits
        // ========================================================

        send_byte(f12[7:0]);
        send_byte(f12[15:8]);
        send_byte({3'b000, f12[20:16]});

        check_feature(4'd12, {{6{1'b0}}, f12});


        // ========================================================
        // FEATURE 13
        // Bwd Header Length
        // 21 bits
        // ========================================================

        send_byte(f13[7:0]);
        send_byte(f13[15:8]);
        send_byte({3'b000, f13[20:16]});

        check_feature(4'd13, {{6{1'b0}}, f13});


        // ========================================================
        // FEATURE 14
        // Flow Duration
        // 27 bits
        // ========================================================

        send_byte(f14[7:0]);
        send_byte(f14[15:8]);
        send_byte(f14[23:16]);
        send_byte({5'b00000, f14[26:24]});

        check_feature(4'd14, f14);


        // ========================================================
        // FEATURE 15
        // Fwd Header Length
        // 21 bits
        // ========================================================

        send_byte(f15[7:0]);
        send_byte(f15[15:8]);
        send_byte({3'b000, f15[20:16]});

        check_feature(4'd15, {{6{1'b0}}, f15});


        // ========================================================
        // FOOTER
        // ========================================================

        send_byte(8'h55);


        // Give DUT time to generate packet_done
        @(posedge clk);


        // ========================================================
        // Check packet_done
        // ========================================================

        if (packet_done !== 1'b1) begin

            $display("ERROR: packet_done was not asserted.");

            errors = errors + 1;

        end
        else begin

            $display("PASS: packet_done asserted.");

        end


        // packet_error must remain low
        if (packet_error !== 1'b0) begin

            $display("ERROR: packet_error asserted unexpectedly.");

            errors = errors + 1;

        end
        else begin

            $display("PASS: packet_error remained LOW.");

        end


        // ========================================================
        // Final result
        // ========================================================

        $display("");
        $display("============================================================");

        if (errors == 0) begin

            $display(" ALL TESTS PASSED");
            $display(" 16/16 features decoded correctly");
            $display(" Packet footer detected correctly");
            $display(" No packet error");
            $display("============================================================");

        end
        else begin

            $display(" TEST FAILED");
            $display(" Errors = %0d", errors);
            $display("============================================================");

        end


        #50;

        $finish;

    end


    // ============================================================
    // Monitor every feature_valid pulse
    // ============================================================

    always @(posedge clk) begin

        if (feature_valid) begin

            feature_count = feature_count + 1;

            $display(
                "  Feature pulse: index=%0d value=%0d (0x%h)",
                feature_index,
                feature_in,
                feature_in
            );

        end

    end

endmodule