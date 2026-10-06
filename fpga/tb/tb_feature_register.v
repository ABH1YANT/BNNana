`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/13/2026 05:37:42 PM
// Design Name: 
// Module Name: tb_feature_register
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

module tb_feature_register_raw;

    reg         clk;
    reg         rst;
    reg         load;
    reg  [3:0]  feature_index;
    reg  [26:0] feature_in;

    wire [277:0] features;

    integer pass_count;
    integer fail_count;

    // ------------------------------------------------------------
    // DUT
    // ------------------------------------------------------------

    feature_register dut (
        .clk(clk),
        .rst(rst),
        .load(load),
        .feature_index(feature_index),
        .feature_in(feature_in),
        .features(features)
    );

    // ------------------------------------------------------------
    // Clock
    // ------------------------------------------------------------

    always #5 clk = ~clk;

    // ------------------------------------------------------------
    // Load one feature
    // ------------------------------------------------------------

    task load_feature;

        input [3:0] index;
        input [26:0] value;

        begin

            @(negedge clk);

            feature_index = index;
            feature_in    = value;
            load          = 1'b1;

            @(posedge clk);

            #1;

            load = 1'b0;

        end

    endtask

    // ------------------------------------------------------------
    // Main test
    // ------------------------------------------------------------

    initial begin

        clk = 1'b0;
        rst = 1'b1;
        load = 1'b0;
        feature_index = 4'd0;
        feature_in = 27'd0;

        pass_count = 0;
        fail_count = 0;

        $display("");
        $display("==============================================");
        $display(" RAW FEATURE REGISTER TEST");
        $display(" 16 FEATURES / 278 BITS");
        $display("==============================================");
        $display("");

        // Reset
        @(posedge clk);
        #1;

        rst = 1'b0;

        // --------------------------------------------------------
        // Load distinctive values into every feature.
        // Values fit their respective widths.
        // --------------------------------------------------------

        load_feature(4'd0, 27'd12000);       // 14-bit
        load_feature(4'd1, 27'd1472);        // 11-bit
        load_feature(4'd2, 27'd16777216);    // 25-bit
        load_feature(4'd3, 27'd12345678);    // 25-bit
        load_feature(4'd4, 27'd65535);       // 16-bit
        load_feature(4'd5, 27'd1480);        // 11-bit
        load_feature(4'd6, 27'd1);            // 1-bit
        load_feature(4'd7, 27'd100000);      // 17-bit
        load_feature(4'd8, 27'd23360);       // 15-bit
        load_feature(4'd9, 27'd99999);       // 17-bit
        load_feature(4'd10, 27'd1323378);    // 21-bit
        load_feature(4'd11, 27'd23360);      // 15-bit
        load_feature(4'd12, 27'd1000000);    // 21-bit
        load_feature(4'd13, 27'd1048576);    // 21-bit
        load_feature(4'd14, 27'd119999877);  // 27-bit
        load_feature(4'd15, 27'd1048576);    // 21-bit

        #10;

        // --------------------------------------------------------
        // Check each packed field
        // --------------------------------------------------------

        if (features[13:0] == 14'd12000) begin
            $display("F0  PASS = %d", features[13:0]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F0  FAIL = %d", features[13:0]);
            fail_count = fail_count + 1;
        end

        if (features[24:14] == 11'd1472) begin
            $display("F1  PASS = %d", features[24:14]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F1  FAIL = %d", features[24:14]);
            fail_count = fail_count + 1;
        end

        if (features[49:25] == 25'd16777216) begin
            $display("F2  PASS = %d", features[49:25]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F2  FAIL = %d", features[49:25]);
            fail_count = fail_count + 1;
        end

        if (features[74:50] == 25'd12345678) begin
            $display("F3  PASS = %d", features[74:50]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F3  FAIL = %d", features[74:50]);
            fail_count = fail_count + 1;
        end

        if (features[90:75] == 16'd65535) begin
            $display("F4  PASS = %d", features[90:75]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F4  FAIL = %d", features[90:75]);
            fail_count = fail_count + 1;
        end

        if (features[101:91] == 11'd1480) begin
            $display("F5  PASS = %d", features[101:91]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F5  FAIL = %d", features[101:91]);
            fail_count = fail_count + 1;
        end

        if (features[102] == 1'b1) begin
            $display("F6  PASS = %b", features[102]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F6  FAIL = %b", features[102]);
            fail_count = fail_count + 1;
        end

        if (features[119:103] == 17'd100000) begin
            $display("F7  PASS = %d", features[119:103]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F7  FAIL = %d", features[119:103]);
            fail_count = fail_count + 1;
        end

        if (features[134:120] == 15'd23360) begin
            $display("F8  PASS = %d", features[134:120]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F8  FAIL = %d", features[134:120]);
            fail_count = fail_count + 1;
        end

        if (features[151:135] == 17'd99999) begin
            $display("F9  PASS = %d", features[151:135]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F9  FAIL = %d", features[151:135]);
            fail_count = fail_count + 1;
        end

        if (features[172:152] == 21'd1323378) begin
            $display("F10 PASS = %d", features[172:152]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F10 FAIL = %d", features[172:152]);
            fail_count = fail_count + 1;
        end

        if (features[187:173] == 15'd23360) begin
            $display("F11 PASS = %d", features[187:173]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F11 FAIL = %d", features[187:173]);
            fail_count = fail_count + 1;
        end

        if (features[208:188] == 21'd1000000) begin
            $display("F12 PASS = %d", features[208:188]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F12 FAIL = %d", features[208:188]);
            fail_count = fail_count + 1;
        end

        if (features[229:209] == 21'd1048576) begin
            $display("F13 PASS = %d", features[229:209]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F13 FAIL = %d", features[229:209]);
            fail_count = fail_count + 1;
        end

        if (features[256:230] == 27'd119999877) begin
            $display("F14 PASS = %d", features[256:230]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F14 FAIL = %d", features[256:230]);
            fail_count = fail_count + 1;
        end

        if (features[277:257] == 21'd1048576) begin
            $display("F15 PASS = %d", features[277:257]);
            pass_count = pass_count + 1;
        end
        else begin
            $display("F15 FAIL = %d", features[277:257]);
            fail_count = fail_count + 1;
        end

        // --------------------------------------------------------
        // Summary
        // --------------------------------------------------------

        $display("");
        $display("==============================================");
        $display("PASS = %0d", pass_count);
        $display("FAIL = %0d", fail_count);
        $display("==============================================");

        if (fail_count == 0)
            $display("RAW FEATURE REGISTER TEST PASSED");
        else
            $display("RAW FEATURE REGISTER TEST FAILED");

        $display("");

        #20;
        $finish;

    end

endmodule