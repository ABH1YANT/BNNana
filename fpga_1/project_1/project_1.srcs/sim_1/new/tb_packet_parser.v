`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/28/2026 12:50:35 AM
// Design Name: 
// Module Name: tb_packet_parser
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

module tb_packet_parser;

    reg         clk;
    reg         rst;

    reg  [7:0]  rx_data;
    reg         rx_valid;

    wire [3:0]  feature_index;
    wire [26:0] feature_in;
    wire        feature_valid;

    wire        packet_done;
    wire        packet_error;

    integer pass_count;
    integer fail_count;

    // ------------------------------------------------------------
    // DUT
    // ------------------------------------------------------------

    packet_parser dut (
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

    always #5 clk = ~clk;


    // ------------------------------------------------------------
    // Send one byte
    // ------------------------------------------------------------

    task send_byte;
        input [7:0] data;

        begin
            @(negedge clk);

            rx_data  = data;
            rx_valid = 1'b1;

            @(negedge clk);

            rx_valid = 1'b0;

            #1;
        end
    endtask


    // ------------------------------------------------------------
    // Check feature
    //
    // IMPORTANT:
    // feature_valid is a one-clock pulse.
    // send_byte() returns immediately after the clock that
    // processed the byte, so we check it HERE rather than
    // waiting for another posedge.
    // ------------------------------------------------------------

    task check_feature;
        input [3:0]  expected_index;
        input [26:0] expected_value;

        begin

            #1;

            if ((feature_valid === 1'b1) &&
                (feature_index === expected_index) &&
                (feature_in === expected_value)) begin

                $display(
                    "F%0d PASS = %0d",
                    expected_index,
                    feature_in
                );

                pass_count = pass_count + 1;

            end
            else begin

                $display(
                    "F%0d FAIL",
                    expected_index
                );

                $display(
                    "  VALID    = %b",
                    feature_valid
                );

                $display(
                    "  INDEX    = %0d",
                    feature_index
                );

                $display(
                    "  VALUE    = %0d",
                    feature_in
                );

                $display(
                    "  EXPECTED = %0d",
                    expected_value
                );

                fail_count = fail_count + 1;

            end

        end
    endtask


    // ------------------------------------------------------------
    // Main test
    // ------------------------------------------------------------

    initial begin

        clk        = 1'b0;
        rst        = 1'b1;
        rx_data    = 8'd0;
        rx_valid   = 1'b0;

        pass_count = 0;
        fail_count = 0;


        $display("");
        $display("==============================================");
        $display(" PACKET PARSER TEST");
        $display(" LITTLE-ENDIAN / 43 PAYLOAD BYTES");
        $display("==============================================");
        $display("");


        // --------------------------------------------------------
        // RESET
        // --------------------------------------------------------

        #20;
        rst = 1'b0;
        #10;


        // --------------------------------------------------------
        // HEADER
        // --------------------------------------------------------

        send_byte(8'hAA);


        // --------------------------------------------------------
        // F0
        // 12000 = 0x2EE0
        // E0 2E
        // --------------------------------------------------------

        send_byte(8'hE0);
        send_byte(8'h2E);

        check_feature(4'd0, 27'd12000);


        // --------------------------------------------------------
        // F1
        // 1472 = 0x05C0
        // C0 05
        // --------------------------------------------------------

        send_byte(8'hC0);
        send_byte(8'h05);

        check_feature(4'd1, 27'd1472);


        // --------------------------------------------------------
        // F2
        // 16777216 = 0x01000000
        // 00 00 00 01
        // --------------------------------------------------------

        send_byte(8'h00);
        send_byte(8'h00);
        send_byte(8'h00);
        send_byte(8'h01);

        check_feature(4'd2, 27'd16777216);


        // --------------------------------------------------------
        // F3
        // 12345678 = 0x00BC614E
        // 4E 61 BC 00
        // --------------------------------------------------------

        send_byte(8'h4E);
        send_byte(8'h61);
        send_byte(8'hBC);
        send_byte(8'h00);

        check_feature(4'd3, 27'd12345678);


        // --------------------------------------------------------
        // F4
        // 65535 = 0xFFFF
        // FF FF
        // --------------------------------------------------------

        send_byte(8'hFF);
        send_byte(8'hFF);

        check_feature(4'd4, 27'd65535);


        // --------------------------------------------------------
        // F5
        // 1480 = 0x05C8
        // C8 05
        // --------------------------------------------------------

        send_byte(8'hC8);
        send_byte(8'h05);

        check_feature(4'd5, 27'd1480);


        // --------------------------------------------------------
        // F6
        // 1
        // --------------------------------------------------------

        send_byte(8'h01);

        check_feature(4'd6, 27'd1);


        // --------------------------------------------------------
        // F7
        // 100000 = 0x0186A0
        // A0 86 01
        // --------------------------------------------------------

        send_byte(8'hA0);
        send_byte(8'h86);
        send_byte(8'h01);

        check_feature(4'd7, 27'd100000);


        // --------------------------------------------------------
        // F8
        // 23360 = 0x5B40
        // 40 5B
        // --------------------------------------------------------

        send_byte(8'h40);
        send_byte(8'h5B);

        check_feature(4'd8, 27'd23360);


        // --------------------------------------------------------
        // F9
        // 99999 = 0x01869F
        // 9F 86 01
        // --------------------------------------------------------

        send_byte(8'h9F);
        send_byte(8'h86);
        send_byte(8'h01);

        check_feature(4'd9, 27'd99999);


        // --------------------------------------------------------
        // F10
        // 1323378 = 0x143172
        // 72 31 14
        // --------------------------------------------------------

        send_byte(8'h72);
        send_byte(8'h31);
        send_byte(8'h14);

        check_feature(4'd10, 27'd1323378);


        // --------------------------------------------------------
        // F11
        // 23360 = 0x5B40
        // 40 5B
        // --------------------------------------------------------

        send_byte(8'h40);
        send_byte(8'h5B);

        check_feature(4'd11, 27'd23360);


        // --------------------------------------------------------
        // F12
        // 1000000 = 0x0F4240
        // 40 42 0F
        // --------------------------------------------------------

        send_byte(8'h40);
        send_byte(8'h42);
        send_byte(8'h0F);

        check_feature(4'd12, 27'd1000000);


        // --------------------------------------------------------
        // F13
        // 1048576 = 0x100000
        // 00 00 10
        // --------------------------------------------------------

        send_byte(8'h00);
        send_byte(8'h00);
        send_byte(8'h10);

        check_feature(4'd13, 27'd1048576);


        // --------------------------------------------------------
        // F14
        // 119999877 = 0x07270D85
        // 85 0D 27 07
        // --------------------------------------------------------

        send_byte(8'h85);
        send_byte(8'h0D);
        send_byte(8'h27);
        send_byte(8'h07);

        check_feature(4'd14, 27'd119999877);


        // --------------------------------------------------------
        // F15
        // 1048576 = 0x100000
        // 00 00 10
        // --------------------------------------------------------

        send_byte(8'h00);
        send_byte(8'h00);
        send_byte(8'h10);

        check_feature(4'd15, 27'd1048576);


        // --------------------------------------------------------
        // FOOTER
        // --------------------------------------------------------

        send_byte(8'h55);


        // packet_done is also a one-clock pulse.
        // Check immediately after send_byte().
        // --------------------------------------------------------

        #1;

        if (packet_done === 1'b1) begin

            $display("PACKET DONE PASS");
            pass_count = pass_count + 1;

        end
        else begin

            $display("PACKET DONE FAIL");
            fail_count = fail_count + 1;

        end


        // --------------------------------------------------------
        // PACKET ERROR
        // --------------------------------------------------------

        if (packet_error === 1'b0) begin

            $display("PACKET ERROR PASS");
            pass_count = pass_count + 1;

        end
        else begin

            $display("PACKET ERROR FAIL");
            fail_count = fail_count + 1;

        end


        // --------------------------------------------------------
        // FINAL RESULT
        // --------------------------------------------------------

        $display("");
        $display("==============================================");
        $display("PASS = %0d", pass_count);
        $display("FAIL = %0d", fail_count);
        $display("==============================================");

        if (fail_count == 0)
            $display("PACKET PARSER TEST PASSED");
        else
            $display("PACKET PARSER TEST FAILED");

        $display("");

        #20;
        $finish;

    end

endmodule
