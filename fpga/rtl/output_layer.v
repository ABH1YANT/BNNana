`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// BNNana
// Output Layer
//
// Architecture:
//     160 binary inputs -> 1 binary output
//
// RTL packed input:
//     inputs[159:96] = Layer 0
//     inputs[95:32]  = Layer 1
//     inputs[31:0]   = Layer 2
//
// IMPORTANT:
//
// The RTL activation registers use bit 0 for the first logical
// Python activation bit.
//
// Therefore the Python-exported 160-bit weight must be represented
// with each activation group reversed:
//
//     Layer 0 : 64 bits
//     Layer 1 : 64 bits
//     Layer 2 : 32 bits
//
// The resulting Verilog weight is:
//
//     5F5142B50E3E67CFA5960CF68633F2CDFCF2B99C
//
// Operation:
//     Fixed-weight XNOR
//     -> 160-bit match vector
//     -> popcount
//     -> threshold
//     -> 1-bit output
//////////////////////////////////////////////////////////////////////////////////

module output_layer #(
    parameter INPUT_COUNT = 160
)(
    input wire clk,
    input wire rst,
    input wire enable,

    input wire [INPUT_COUNT-1:0] inputs,

    output reg output_bit,
    output reg done
);

    // ============================================================
    // OUTPUT WEIGHT
    //
    // Python-exported weight:
    //
    // F3E67C70AD428AFAB34FCC616F3069A5399D4F3F
    //
    // Python groups:
    //
    //   Layer 0 = F3E67C70AD428AFA
    //   Layer 1 = B34FCC616F3069A5
    //   Layer 2 = 399D4F3F
    //
    // Each group is reversed for the RTL bit indexing convention.
    //
    // RTL weight:
    //
    //   Layer 0 = 5F5142B50E3E67CF
    //   Layer 1 = A5960CF68633F2CD
    //   Layer 2 = FCF2B99C
    //
    // Combined:
    //
    //   5F5142B50E3E67CFA5960CF68633F2CDFCF2B99C
    // ============================================================

    wire [159:0] weights;

    assign weights =
        160'h5F5142B50E3E67CFA5960CF68633F2CDFCF2B99C;


    // ============================================================
    // OUTPUT THRESHOLD
    //
    // Python threshold:
    //     0051 = 81
    //
    // Final binary linear layer:
    //
    //     logit = 2 * match_count - 160
    //
    // Python classification:
    //
    //     logit > 0
    //
    // Therefore:
    //
    //     match_count > 80
    //
    // Equivalent integer comparison:
    //
    //     match_count >= 81
    // ============================================================

    wire [7:0] threshold;

    assign threshold = 8'd81;


    // ============================================================
    // PIPELINE REGISTERS
    // ============================================================

    // Stage 1: 160 registered XNOR results
    reg [159:0] match_reg;

    // Stage 2: 80 groups of 2
    reg [159:0] pair_count;

    // Stage 3: 40 groups of 4
    reg [119:0] quad_count;

    // Stage 4: 20 groups of 8
    reg [79:0] oct_count;

    // Stage 5: 10 groups of 16
    reg [49:0] sixteen_count;

    // Stage 6: 5 groups of 32
    reg [29:0] thirtytwo_count;

    // Stage 7: 2 groups of 64 + one remaining group of 32
    reg [13:0] sixtyfour_count;
    reg [5:0] last_group_count;

    // Stage 8: Sum of the two 64-bit groups
    reg [7:0] count128;
    reg [5:0] delayed_group32;

    // Stage 9: Final 160-bit popcount
    reg [7:0] total_count;

    // Pipeline valid signals
    reg valid1;
    reg valid2;
    reg valid3;
    reg valid4;
    reg valid5;
    reg valid6;
    reg valid7;
    reg valid8;
    reg valid9;

    integer j;


    // ============================================================
    // TEN-STAGE PIPELINE
    // ============================================================

    always @(posedge clk) begin

        if (rst) begin

            output_bit <= 1'b0;
            done <= 1'b0;

            valid1 <= 1'b0;
            valid2 <= 1'b0;
            valid3 <= 1'b0;
            valid4 <= 1'b0;
            valid5 <= 1'b0;
            valid6 <= 1'b0;
            valid7 <= 1'b0;
            valid8 <= 1'b0;
            valid9 <= 1'b0;

            match_reg <= 160'd0;
            pair_count <= 160'd0;
            quad_count <= 120'd0;
            oct_count <= 80'd0;
            sixteen_count <= 50'd0;
            thirtytwo_count <= 30'd0;
            sixtyfour_count <= 14'd0;
            last_group_count <= 6'd0;
            count128 <= 8'd0;
            delayed_group32 <= 6'd0;
            total_count <= 8'd0;

        end

        else begin

            // ----------------------------------------------------
            // VALID PIPELINE
            // ----------------------------------------------------

            valid1 <= enable;
            valid2 <= valid1;
            valid3 <= valid2;
            valid4 <= valid3;
            valid5 <= valid4;
            valid6 <= valid5;
            valid7 <= valid6;
            valid8 <= valid7;
            valid9 <= valid8;

            done <= valid9;


            // ----------------------------------------------------
            // STAGE 1: XNOR
            // ----------------------------------------------------

            if (enable) begin
                match_reg <= ~(inputs ^ weights);
            end


            // ----------------------------------------------------
            // STAGE 2: 160 BITS -> 80 PAIR COUNTS
            // ----------------------------------------------------

            if (valid1) begin
                for (j = 0; j < 80; j = j + 1) begin
                    pair_count[2*j +: 2] <=
                        {1'b0, match_reg[2*j]} +
                        {1'b0, match_reg[2*j+1]};
                end
            end


            // ----------------------------------------------------
            // STAGE 3: 80 PAIRS -> 40 GROUPS OF 4
            // ----------------------------------------------------

            if (valid2) begin
                for (j = 0; j < 40; j = j + 1) begin
                    quad_count[3*j +: 3] <=
                        {1'b0, pair_count[4*j +: 2]} +
                        {1'b0, pair_count[4*j+2 +: 2]};
                end
            end


            // ----------------------------------------------------
            // STAGE 4: 40 GROUPS OF 4 -> 20 GROUPS OF 8
            // ----------------------------------------------------

            if (valid3) begin
                for (j = 0; j < 20; j = j + 1) begin
                    oct_count[4*j +: 4] <=
                        {1'b0, quad_count[6*j +: 3]} +
                        {1'b0, quad_count[6*j+3 +: 3]};
                end
            end


            // ----------------------------------------------------
            // STAGE 5: 20 GROUPS OF 8 -> 10 GROUPS OF 16
            // ----------------------------------------------------

            if (valid4) begin
                for (j = 0; j < 10; j = j + 1) begin
                    sixteen_count[5*j +: 5] <=
                        {1'b0, oct_count[8*j +: 4]} +
                        {1'b0, oct_count[8*j+4 +: 4]};
                end
            end


            // ----------------------------------------------------
            // STAGE 6: 10 GROUPS OF 16 -> 5 GROUPS OF 32
            // ----------------------------------------------------

            if (valid5) begin
                for (j = 0; j < 5; j = j + 1) begin
                    thirtytwo_count[6*j +: 6] <=
                        {1'b0, sixteen_count[10*j +: 5]} +
                        {1'b0, sixteen_count[10*j+5 +: 5]};
                end
            end


            // ----------------------------------------------------
            // STAGE 7: 5 GROUPS OF 32 -> 2 GROUPS OF 64
            // The fifth group remains as a separate 32-bit count.
            // ----------------------------------------------------

            if (valid6) begin

                sixtyfour_count[6:0] <=
                    {1'b0, thirtytwo_count[5:0]} +
                    {1'b0, thirtytwo_count[11:6]};

                sixtyfour_count[13:7] <=
                    {1'b0, thirtytwo_count[17:12]} +
                    {1'b0, thirtytwo_count[23:18]};

                last_group_count <= thirtytwo_count[29:24];

            end


            // ----------------------------------------------------
            // STAGE 8: SUM THE TWO 64-BIT GROUPS
            // Delay the remaining 32-bit group.
            // ----------------------------------------------------

            if (valid7) begin

                count128 <=
                    {1'b0, sixtyfour_count[6:0]} +
                    {1'b0, sixtyfour_count[13:7]};

                delayed_group32 <= last_group_count;

            end


            // ----------------------------------------------------
            // STAGE 9: FINAL 160-BIT POPCOUNT
            // ----------------------------------------------------

            if (valid8) begin

                total_count <=
                    count128 + {2'b00, delayed_group32};

            end


            // ----------------------------------------------------
            // STAGE 10: THRESHOLD COMPARISON
            // ----------------------------------------------------

            if (valid9) begin

                output_bit <= (total_count >= threshold);

            end

        end
    end

endmodule
