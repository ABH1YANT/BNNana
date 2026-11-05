`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/27/2026 12:32:27 PM
// Design Name: 
// Module Name: hidden_layer_2
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

//////////////////////////////////////////////////////////////////////////////////
// BNNana
// Layer 2
//
// Architecture:
//     128 binary inputs -> 32 binary outputs
//
// Input:
//     Layer 1 output = 64 bits
//     Layer 0 output = 64 bits
//     Total          = 128 bits
//
// Weights:
//     32 neurons x 128 binary weights
//     Hardcoded constants - NOT BRAM
//
// Thresholds:
//     32 integer popcount thresholds
//     Popcount range = 0..128
//     Hardcoded constants - NOT BRAM
//
// Operation:
//     Fixed-weight XNOR
//     -> 128-bit match vector
//     -> popcount
//     -> integer threshold
//     -> binary output
//////////////////////////////////////////////////////////////////////////////////

module hidden_layer_2 #(
    parameter INPUT_COUNT  = 128,
    parameter OUTPUT_COUNT = 32
)(
    input  wire                  clk,
    input  wire                  rst,
    input  wire                  start,
    input  wire [INPUT_COUNT-1:0] inputs,

    output reg  [OUTPUT_COUNT-1:0] outputs,
    output reg                   done
);

    // ============================================================
    // ACTUAL TRAINED LAYER 2 WEIGHTS
    //
    // 32 neurons x 128 binary weights
    //
    // These are HARDWARE CONSTANTS.
    // They are NOT stored in BRAM.
    // ============================================================

    wire [127:0] weights [0:31];

    assign weights[0]  = 128'h62B4EFD5CD1E12DA1B27D460B405AC70;
    assign weights[1]  = 128'hF0327178697AFFA5EE0473A489F4B70C;
    assign weights[2]  = 128'h9D2B112F56176504EC826B92C3E84293;
    assign weights[3]  = 128'h9D29902F12AD6405F7892398ED6F43CB;
    assign weights[4]  = 128'hF2966FC4AD3692FA917CD54E340AB860;
    assign weights[5]  = 128'h9D6B116856C5C464EEE87F9F6BDED69B;
    assign weights[6]  = 128'h9D21912B52376524EEB82B9BEBCC029F;
    assign weights[7]  = 128'h0FCD8E9396A5214A81BE984AEE2B3C51;
    assign weights[8]  = 128'h0FAD8783DEA5257A00FF9E5AEB3B58D1;
    assign weights[9]  = 128'hF132756C6952DB957F2D2BB115E4027E;
    assign weights[10] = 128'h7294E4D5ED12BEF3311DC4630D361965;
    assign weights[11] = 128'h1D29902D1EFB692CE4C16795EEC9A28F;
    assign weights[12] = 128'hE3D52EC4A11292F212358C41B7352A20;
    assign weights[13] = 128'h0FED8E9396AD24CC80FA9807EE6B18F3;
    assign weights[14] = 128'h9D4B913B53EDE10C7CD0378E73EA538A;
    assign weights[15] = 128'h1D29917F52CD4C64E5E865AA62F1D2DB;
    assign weights[16] = 128'h7032F16C695ADFA577E573F41D84A70C;
    assign weights[17] = 128'h62D46CD5ED5A26DB9874D0401A34A834;
    assign weights[18] = 128'h9D19133B5EC1652466C2258BEFCED7CB;
    assign weights[19] = 128'hF072756C6952D6855E4371E410B4264F;
    assign weights[20] = 128'h62D62EC4E130BEF31117D8401421F8B9;
    assign weights[21] = 128'h72B4656464709BFB122FC67CF4365870;
    assign weights[22] = 128'h0FCD8E939685284AA19D881BF54B5AD3;
    assign weights[23] = 128'hC2DEEFD6AD1616D3113E886216300B34;
    assign weights[24] = 128'h9D23113A120DE904EFC12333E9CA57CB;
    assign weights[25] = 128'h3D29113A52F76DECEFE02209E9FC11DB;
    assign weights[26] = 128'h9D2B193A14C5D024CFD9279CEB4712DB;
    assign weights[27] = 128'h62D6EED4ED3A92DE1904D0E451058A20;
    assign weights[28] = 128'h0F8D8A8396A5247A829A9A4EF30B3990;
    assign weights[29] = 128'h9D29D12D529D492CE6C32BA8E9CD76CB;
    assign weights[30] = 128'h62967CD4AB78BFFB001CC9611A3ED970;
    assign weights[31] = 128'h72DE6ED5AD1896FB3307D8CE961599B4;


    // ============================================================
    // ACTUAL TRAINED LAYER 2 THRESHOLDS
    //
    // Popcount range = 0..128
    // Therefore threshold width = 8 bits.
    //
    // These are HARDWARE CONSTANTS.
    // ============================================================

    wire [7:0] thresholds [0:31];

    assign thresholds[0]  = 8'd56;
    assign thresholds[1]  = 8'd58;
    assign thresholds[2]  = 8'd78;
    assign thresholds[3]  = 8'd77;
    assign thresholds[4]  = 8'd63;
    assign thresholds[5]  = 8'd66;
    assign thresholds[6]  = 8'd43;
    assign thresholds[7]  = 8'd70;
    assign thresholds[8]  = 8'd67;
    assign thresholds[9]  = 8'd61;
    assign thresholds[10] = 8'd58;
    assign thresholds[11] = 8'd68;
    assign thresholds[12] = 8'd71;
    assign thresholds[13] = 8'd67;
    assign thresholds[14] = 8'd58;
    assign thresholds[15] = 8'd64;
    assign thresholds[16] = 8'd59;
    assign thresholds[17] = 8'd81;
    assign thresholds[18] = 8'd59;
    assign thresholds[19] = 8'd63;
    assign thresholds[20] = 8'd59;
    assign thresholds[21] = 8'd63;
    assign thresholds[22] = 8'd72;
    assign thresholds[23] = 8'd63;
    assign thresholds[24] = 8'd73;
    assign thresholds[25] = 8'd67;
    assign thresholds[26] = 8'd123;
    assign thresholds[27] = 8'd54;
    assign thresholds[28] = 8'd70;
    assign thresholds[29] = 8'd61;
    assign thresholds[30] = 8'd50;
    assign thresholds[31] = 8'd70;


    // ============================================================
    // PIPELINE REGISTERS
    // ============================================================

    // Stage 1: Registered XNOR match vectors
    reg [127:0] match_reg [0:31];

    // Stage 2: 64 pairwise counts, 2 bits each
    reg [127:0] pair_count [0:31];

    // Stage 3: 32 groups of 4, 3 bits each
    reg [95:0] quad_count [0:31];

    // Stage 4: 16 groups of 8, 4 bits each
    reg [63:0] oct_count [0:31];

    // Stage 5: 8 groups of 16, 5 bits each
    reg [39:0] sixteen_count [0:31];

    // Stage 6: 4 groups of 32, 6 bits each
    reg [23:0] thirtytwo_count [0:31];

    // Stage 7: 2 groups of 64, 7 bits each
    reg [13:0] sixtyfour_count [0:31];

    // Stage 8: Final 128-bit count
    reg [7:0] total_count [0:31];

    // Pipeline valid signals
    reg valid1;
    reg valid2;
    reg valid3;
    reg valid4;
    reg valid5;
    reg valid6;
    reg valid7;
    reg valid8;

    integer k;
    integer j;


    // ============================================================
    // NINE-STAGE PIPELINE
    // ============================================================

    always @(posedge clk) begin

        if (rst) begin

            outputs <= {OUTPUT_COUNT{1'b0}};
            done <= 1'b0;

            valid1 <= 1'b0;
            valid2 <= 1'b0;
            valid3 <= 1'b0;
            valid4 <= 1'b0;
            valid5 <= 1'b0;
            valid6 <= 1'b0;
            valid7 <= 1'b0;
            valid8 <= 1'b0;

            for (k = 0; k < OUTPUT_COUNT; k = k + 1) begin
                match_reg[k]      <= 128'd0;
                pair_count[k]     <= 128'd0;
                quad_count[k]     <= 96'd0;
                oct_count[k]      <= 64'd0;
                sixteen_count[k]  <= 40'd0;
                thirtytwo_count[k] <= 24'd0;
                sixtyfour_count[k] <= 14'd0;
                total_count[k]    <= 8'd0;
            end

        end

        else begin

            // ----------------------------------------------------
            // PIPELINE VALID CONTROL
            // ----------------------------------------------------

            valid1 <= start;
            valid2 <= valid1;
            valid3 <= valid2;
            valid4 <= valid3;
            valid5 <= valid4;
            valid6 <= valid5;
            valid7 <= valid6;
            valid8 <= valid7;

            done <= valid8;


            // ----------------------------------------------------
            // STAGE 1: XNOR
            // ----------------------------------------------------

            if (start) begin
                for (k = 0; k < OUTPUT_COUNT; k = k + 1) begin
                    match_reg[k] <= ~(inputs ^ weights[k]);
                end
            end


            // ----------------------------------------------------
            // STAGE 2: 128 BITS -> 64 PAIR COUNTS
            // ----------------------------------------------------

            if (valid1) begin
                for (k = 0; k < OUTPUT_COUNT; k = k + 1) begin
                    for (j = 0; j < 64; j = j + 1) begin
                        pair_count[k][2*j +: 2] <=
                            {1'b0, match_reg[k][2*j]} +
                            {1'b0, match_reg[k][2*j+1]};
                    end
                end
            end


            // ----------------------------------------------------
            // STAGE 3: 64 PAIR COUNTS -> 32 GROUPS OF 4
            // ----------------------------------------------------

            if (valid2) begin
                for (k = 0; k < OUTPUT_COUNT; k = k + 1) begin
                    for (j = 0; j < 32; j = j + 1) begin
                        quad_count[k][3*j +: 3] <=
                            {1'b0, pair_count[k][4*j +: 2]} +
                            {1'b0, pair_count[k][4*j+2 +: 2]};
                    end
                end
            end


            // ----------------------------------------------------
            // STAGE 4: 32 GROUPS OF 4 -> 16 GROUPS OF 8
            // ----------------------------------------------------

            if (valid3) begin
                for (k = 0; k < OUTPUT_COUNT; k = k + 1) begin
                    for (j = 0; j < 16; j = j + 1) begin
                        oct_count[k][4*j +: 4] <=
                            {1'b0, quad_count[k][6*j +: 3]} +
                            {1'b0, quad_count[k][6*j+3 +: 3]};
                    end
                end
            end


            // ----------------------------------------------------
            // STAGE 5: 16 GROUPS OF 8 -> 8 GROUPS OF 16
            // ----------------------------------------------------

            if (valid4) begin
                for (k = 0; k < OUTPUT_COUNT; k = k + 1) begin
                    for (j = 0; j < 8; j = j + 1) begin
                        sixteen_count[k][5*j +: 5] <=
                            {1'b0, oct_count[k][8*j +: 4]} +
                            {1'b0, oct_count[k][8*j+4 +: 4]};
                    end
                end
            end


            // ----------------------------------------------------
            // STAGE 6: 8 GROUPS OF 16 -> 4 GROUPS OF 32
            // ----------------------------------------------------

            if (valid5) begin
                for (k = 0; k < OUTPUT_COUNT; k = k + 1) begin
                    for (j = 0; j < 4; j = j + 1) begin
                        thirtytwo_count[k][6*j +: 6] <=
                            {1'b0, sixteen_count[k][10*j +: 5]} +
                            {1'b0, sixteen_count[k][10*j+5 +: 5]};
                    end
                end
            end


            // ----------------------------------------------------
            // STAGE 7: 4 GROUPS OF 32 -> 2 GROUPS OF 64
            // ----------------------------------------------------

            if (valid6) begin
                for (k = 0; k < OUTPUT_COUNT; k = k + 1) begin
                    for (j = 0; j < 2; j = j + 1) begin
                        sixtyfour_count[k][7*j +: 7] <=
                            {1'b0, thirtytwo_count[k][12*j +: 6]} +
                            {1'b0, thirtytwo_count[k][12*j+6 +: 6]};
                    end
                end
            end


            // ----------------------------------------------------
            // STAGE 8: 2 GROUPS OF 64 -> FINAL 128-BIT COUNT
            // ----------------------------------------------------

            if (valid7) begin
                for (k = 0; k < OUTPUT_COUNT; k = k + 1) begin
                    total_count[k] <=
                        {1'b0, sixtyfour_count[k][6:0]} +
                        {1'b0, sixtyfour_count[k][13:7]};
                end
            end


            // ----------------------------------------------------
            // STAGE 9: THRESHOLD COMPARISON
            // ----------------------------------------------------

            if (valid8) begin
                for (k = 0; k < OUTPUT_COUNT; k = k + 1) begin
                    outputs[k] <=
                        (total_count[k] >= thresholds[k]);
                end
            end

        end
    end

endmodule
