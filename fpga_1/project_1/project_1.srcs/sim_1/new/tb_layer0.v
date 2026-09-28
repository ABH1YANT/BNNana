`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/13/2026 11:51:18 PM
// Design Name: 
// Module Name: tb_layer0
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
module tb_layer0;

    reg [127:0] inputs;

    wire [63:0] outputs;

    integer pass_count;
    integer fail_count;


    layer0 dut (
        .inputs(inputs),
        .outputs(outputs)
    );


    task check_output;

        input [63:0] expected;
        input [127:0] test_input;
        input integer test_number;

        begin

            inputs = test_input;

            #10;

            if (outputs === expected) begin

                $display(
                    "TEST %0d: PASS  INPUT=%032h  OUTPUT=%016h",
                    test_number,
                    test_input,
                    outputs
                );

                pass_count = pass_count + 1;

            end
            else begin

                $display(
                    "TEST %0d: FAIL",
                    test_number
                );

                $display(
                    "  INPUT    = %032h",
                    test_input
                );

                $display(
                    "  EXPECTED = %016h",
                    expected
                );

                $display(
                    "  ACTUAL   = %016h",
                    outputs
                );

                fail_count = fail_count + 1;

            end

        end

    endtask


    initial begin

        pass_count = 0;
        fail_count = 0;

        $display("");
        $display("============================================================");
        $display("LAYER 0 TEST");
        $display("16 INPUTS -> 64 BINARY OUTPUTS");
        $display("============================================================");


        // ========================================================
        // TEST 1
        // All Q1.8 inputs = 0
        // ========================================================

        check_output(
            64'h947BCC8F3697082F,
            128'h00000000000000000000000000000000,
            1
        );


        // ========================================================
        // TEST 2
        // All Q1.8 inputs = 255
        // ========================================================

        check_output(
            64'h1820FF54AEC9D6AD,
            128'hFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            2
        );


        // ========================================================
        // TEST 3
        // All Q1.8 inputs = 1
        // ========================================================

        check_output(
            64'h9C7BCC8F3697082F,
            128'h01010101010101010101010101010101,
            3
        );


        // ========================================================
        // TEST 4
        // Inputs = 0,1,2,...,15
        //
        // Remember:
        // input 0 occupies bits [7:0]
        // input 15 occupies bits [127:120]
        // ========================================================

        check_output(
            64'h9C7BCC97369F0A2F,
            128'h0F0E0D0C0B0A09080706050403020100,
            4
        );


        // ========================================================
        // TEST 5
        // Deterministic non-uniform vector
        // ========================================================

        check_output(
            64'h5821FB54AEC9D6AD,
            128'hFFF2E5D8CBBEB1A4978A7D706356493C,
            5
        );


        // ========================================================
        // TEST 6
        // Deterministic random vector
        // ========================================================

        check_output(
            64'h18237B54BE88D6AD,
            128'hD50598BC638ADF52BF3FDD85595FB52E,
            6
        );


        // ========================================================
        // TEST 7
        // Deterministic random vector
        // ========================================================

        check_output(
            64'h1863F8D4378FD4AD,
            128'hD3554B692761AEA40CEAAD0DD4010353,
            7
        );


        // ========================================================
        // TEST 8
        // Deterministic random vector
        // ========================================================

        check_output(
            64'h1823FA54268CD6AD,
            128'h5B9232D4365DC077A814763DFF6E5F83,
            8
        );


        // ========================================================
        // TEST 9
        // Deterministic random vector
        // ========================================================

        check_output(
            64'h9861FBD4AE9AD6AD,
            128'hDE4215549A044C75B3AF50C5A506191F,
            9
        );


        // ========================================================
        // TEST 10
        // Deterministic random vector
        // ========================================================

        check_output(
            64'h1863FB75B4C9D6AD,
            128'hE328C65B05BC6E3EF61F07FBA6D767BA,
            10
        );


        // ========================================================
        // SUMMARY
        // ========================================================

        $display("");
        $display("============================================================");
        $display("LAYER 0 VERIFICATION COMPLETE");
        $display("PASS = %0d", pass_count);
        $display("FAIL = %0d", fail_count);
        $display("============================================================");


        if (fail_count == 0)
            $display("LAYER 0 TEST PASSED");
        else
            $display("LAYER 0 TEST FAILED");


        $display("");

        $finish;

    end

endmodule
