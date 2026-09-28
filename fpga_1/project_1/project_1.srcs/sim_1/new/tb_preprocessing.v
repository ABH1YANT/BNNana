`timescale 1ns / 1ps

module tb_preprocessing_bram;

    reg clk;

    reg [277:0] features;

    wire [127:0] preprocessed;

    integer pass_count;
    integer fail_count;


    // ------------------------------------------------------------
    // DUT
    // ------------------------------------------------------------

    preprocessing dut (
        .clk(clk),
        .features(features),
        .preprocessed(preprocessed)
    );


    // ------------------------------------------------------------
    // Clock
    // ------------------------------------------------------------

    initial begin
        clk = 1'b0;

        forever #5 clk = ~clk;
    end


    // ------------------------------------------------------------
    // Expected value from the SAME ROM contents
    // ------------------------------------------------------------

    reg [7:0] exp_lut0  [0:4095];
    reg [7:0] exp_lut1  [0:1023];
    reg [7:0] exp_lut2  [0:65535];
    reg [7:0] exp_lut3  [0:65535];
    reg [7:0] exp_lut4  [0:4095];
    reg [7:0] exp_lut5  [0:1023];
    reg [7:0] exp_lut6  [0:1];
    reg [7:0] exp_lut7  [0:4095];
    reg [7:0] exp_lut8  [0:4095];
    reg [7:0] exp_lut9  [0:4095];
    reg [7:0] exp_lut10 [0:65535];
    reg [7:0] exp_lut11 [0:4095];
    reg [7:0] exp_lut12 [0:65535];
    reg [7:0] exp_lut13 [0:65535];
    reg [7:0] exp_lut14 [0:65535];
    reg [7:0] exp_lut15 [0:65535];

    reg [127:0] expected;


    // ------------------------------------------------------------
    // Test task
    // ------------------------------------------------------------

    task run_test;

        input [277:0] test_features;

        begin

            features = test_features;

            // ----------------------------------------------------
            // Clock 1:
            // Synchronous BRAM lookup
            // ----------------------------------------------------

            @(posedge clk);
            #1;


            // ----------------------------------------------------
            // Clock 2:
            // Extra preprocessing output register
            // ----------------------------------------------------

            @(posedge clk);
            #1;


            // ----------------------------------------------------
            // Calculate expected LUT result
            // ----------------------------------------------------

            expected = {
                exp_lut15[test_features[277:257] >> 5],
                exp_lut14[test_features[256:230] >> 11],
                exp_lut13[test_features[229:209] >> 5],
                exp_lut12[test_features[208:188] >> 5],
                exp_lut11[test_features[187:173] >> 3],
                exp_lut10[test_features[172:152] >> 5],
                exp_lut9 [test_features[151:135] >> 5],
                exp_lut8 [test_features[134:120] >> 3],
                exp_lut7 [test_features[119:103] >> 5],
                exp_lut6 [test_features[102]],
                exp_lut5 [test_features[101:91] >> 1],
                exp_lut4 [test_features[90:75] >> 4],
                exp_lut3 [test_features[74:50] >> 9],
                exp_lut2 [test_features[49:25] >> 9],
                exp_lut1 [test_features[24:14] >> 1],
                exp_lut0 [test_features[13:0] >> 2]
            };


            // ----------------------------------------------------
            // Compare
            // ----------------------------------------------------

            if (preprocessed === expected) begin

                pass_count = pass_count + 1;

                $display(
                    "PASS = %h",
                    preprocessed
                );

            end
            else begin

                fail_count = fail_count + 1;

                $display("FAIL");

                $display(
                    "Expected = %h",
                    expected
                );

                $display(
                    "Got      = %h",
                    preprocessed
                );

            end

        end

    endtask


    // ------------------------------------------------------------
    // Tests
    // ------------------------------------------------------------

    initial begin

        pass_count = 0;
        fail_count = 0;

        features = 278'd0;


        // --------------------------------------------------------
        // Load expected ROM contents
        // --------------------------------------------------------

        $readmemh(
            "Bwd_Packet_Length_Max.mem",
            exp_lut0
        );

        $readmemh(
            "Min_Packet_Length.mem",
            exp_lut1
        );

        $readmemh(
            "Subflow_Bwd_Bytes.mem",
            exp_lut2
        );

        $readmemh(
            "Total_Length_of_Bwd_Packets.mem",
            exp_lut3
        );

        $readmemh(
            "Destination_Port.mem",
            exp_lut4
        );

        $readmemh(
            "min_seg_size_forward.mem",
            exp_lut5
        );

        $readmemh(
            "ACK_Flag_Count.mem",
            exp_lut6
        );

        $readmemh(
            "Subflow_Bwd_Packets.mem",
            exp_lut7
        );

        $readmemh(
            "Fwd_Packet_Length_Max.mem",
            exp_lut8
        );

        $readmemh(
            "Total_Backward_Packets.mem",
            exp_lut9
        );

        $readmemh(
            "Subflow_Fwd_Bytes.mem",
            exp_lut10
        );

        $readmemh(
            "Max_Packet_Length.mem",
            exp_lut11
        );

        $readmemh(
            "Total_Length_of_Fwd_Packets.mem",
            exp_lut12
        );

        $readmemh(
            "Bwd_Header_Length.mem",
            exp_lut13
        );

        $readmemh(
            "Flow_Duration.mem",
            exp_lut14
        );

        $readmemh(
            "Fwd_Header_Length.mem",
            exp_lut15
        );


        // --------------------------------------------------------
        // Test 1: all zero
        // --------------------------------------------------------

        run_test(278'd0);


        // --------------------------------------------------------
        // Test 2: all maximum
        // --------------------------------------------------------

        run_test({278{1'b1}});


        // --------------------------------------------------------
        // Test 3: alternating pattern
        // --------------------------------------------------------

        run_test(
            278'hAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        );


        // --------------------------------------------------------
        // Test 4: another deterministic pattern
        // --------------------------------------------------------

        run_test(
            278'h1555555555555555555555555555555555555555555555555555555555555555
        );


        // --------------------------------------------------------
        // Test 5: mixed pattern
        // --------------------------------------------------------

        run_test(
            278'h0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCD
        );


        // --------------------------------------------------------
        // Result
        // --------------------------------------------------------

        $display("");
        $display("==============================================");
        $display("BRAM PREPROCESSING TEST RESULT");
        $display("==============================================");

        $display(
            "PASS = %0d",
            pass_count
        );

        $display(
            "FAIL = %0d",
            fail_count
        );

        if (fail_count == 0)
            $display("BRAM PREPROCESSING TEST PASSED");
        else
            $display("BRAM PREPROCESSING TEST FAILED");

        $display("==============================================");

        $finish;

    end

endmodule