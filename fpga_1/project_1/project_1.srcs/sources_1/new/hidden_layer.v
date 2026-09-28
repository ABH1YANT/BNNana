`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/14/2026 12:43:10 AM
// Design Name: 
// Module Name: hidden_layer
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
module hidden_layer #(
    parameter INPUT_COUNT  = 64,
    parameter OUTPUT_COUNT = 64
)(
    input  wire [INPUT_COUNT-1:0]  inputs,
    output wire [OUTPUT_COUNT-1:0] outputs
);

    // ============================================================
    // ACTUAL TRAINED LAYER 1 WEIGHTS
    // 64 neurons × 64 binary weights
    // ============================================================

    wire [63:0] weights [0:63];

    assign weights[0]  = 64'h038FE6CA9D7826FB;
    assign weights[1]  = 64'h156B16EF0ACC4517;
    assign weights[2]  = 64'h03DC2EC6ECAA1FF3;
    assign weights[3]  = 64'hC3CDDC50BA113F77;
    assign weights[4]  = 64'hDD23112B327DE904;
    assign weights[5]  = 64'h116B17AF00CE4413;
    assign weights[6]  = 64'hA29ECE55AD3217F3;
    assign weights[7]  = 64'h62B52741F01A3FF7;
    assign weights[8]  = 64'h7432754C7942F734;
    assign weights[9]  = 64'h62D6FE53AD8693D3;
    assign weights[10] = 64'h5C2959685455E508;
    assign weights[11] = 64'h150B132B1CC67944;
    assign weights[12] = 64'h7D2190395BD5E004;
    assign weights[13] = 64'h0B8D0AD78E8F3CC8;
    assign weights[14] = 64'h229E2617AD889EF3;
    assign weights[15] = 64'h42D62FD3A54A3AFB;
    assign weights[16] = 64'h2022261FCCCC6596;
    assign weights[17] = 64'hE2DCAED7A91A87F3;
    assign weights[18] = 64'h3F942072E5FF984C;
    assign weights[19] = 64'hBD29112D56A9D124;
    assign weights[20] = 64'h439FEE57AC121EFB;
    assign weights[21] = 64'hE296AE57A40A16FB;
    assign weights[22] = 64'h429EEEC2AD162EF3;
    assign weights[23] = 64'h8149832B86F769CA;
    assign weights[24] = 64'h076983A2868760DA;
    assign weights[25] = 64'h0FED8E87968520ED;
    assign weights[26] = 64'h42D6EF42B8A0BAFF;
    assign weights[27] = 64'h3D69103E54B9CC04;
    assign weights[28] = 64'h5D2BD12B14FDD00C;
    assign weights[29] = 64'hDD62593A7365E30C;
    assign weights[30] = 64'h3D2B91395AE5E00C;
    assign weights[31] = 64'h42D6EFD1A90E1EF3;
    assign weights[32] = 64'hC2D6BFD6ACB23A73;
    assign weights[33] = 64'h9D6B113E588BE924;
    assign weights[34] = 64'h3D2851BD1EFB490C;
    assign weights[35] = 64'h0D0B922E48ADF008;
    assign weights[36] = 64'h42DEAE468D8213F3;
    assign weights[37] = 64'h42D6E6C7ED5AB2FB;
    assign weights[38] = 64'h62B7DED2AB28A7F3;
    assign weights[39] = 64'hC3DE2E56AC8217F3;
    assign weights[40] = 64'h2F94212665FE11C4;
    assign weights[41] = 64'hF07AF5687118DA16;
    assign weights[42] = 64'h43DD2F52A84A11F2;
    assign weights[43] = 64'hE3D4AEC3ED98BFFB;
    assign weights[44] = 64'h3D2191BD53E5C804;
    assign weights[45] = 64'hFC21112C13F5C708;
    assign weights[46] = 64'h05499AAB869F605F;
    assign weights[47] = 64'h056F86A386D748DE;
    assign weights[48] = 64'hBD21112E7655E10C;
    assign weights[49] = 64'h82DEAFC6AC921ADB;
    assign weights[50] = 64'h6284AEC1CD82A3BB;
    assign weights[51] = 64'h1D29102853C5E544;
    assign weights[52] = 64'h3E9EE540FB889237;
    assign weights[53] = 64'hDD2B10385F5DE50C;
    assign weights[54] = 64'h3D6841395B3DE104;
    assign weights[55] = 64'h6294BEC7A5821EFB;
    assign weights[56] = 64'h1D6011291AE1490C;
    assign weights[57] = 64'h1D2991AD77E14D04;
    assign weights[58] = 64'h0BCD8AD396E53849;
    assign weights[59] = 64'h63D6AEC2A882B2FB;
    assign weights[60] = 64'h25490B2B37EE6104;
    assign weights[61] = 64'h1D61113F5735E104;
    assign weights[62] = 64'hF472756C695AFA32;
    assign weights[63] = 64'h62F6F6D38D7436FB;


    // ============================================================
    // ACTUAL TRAINED LAYER 1 THRESHOLDS
    // Popcount range = 0..64
    // ============================================================

    wire [6:0] thresholds [0:63];

    assign thresholds[0]  = 7'd28;
    assign thresholds[1]  = 7'd41;
    assign thresholds[2]  = 7'd30;
    assign thresholds[3]  = 7'd28;
    assign thresholds[4]  = 7'd25;
    assign thresholds[5]  = 7'd43;
    assign thresholds[6]  = 7'd30;
    assign thresholds[7]  = 7'd7;
    assign thresholds[8]  = 7'd29;
    assign thresholds[9]  = 7'd37;
    assign thresholds[10] = 7'd38;
    assign thresholds[11] = 7'd34;
    assign thresholds[12] = 7'd23;
    assign thresholds[13] = 7'd37;
    assign thresholds[14] = 7'd48;
    assign thresholds[15] = 7'd18;
    assign thresholds[16] = 7'd32;
    assign thresholds[17] = 7'd64;
    assign thresholds[18] = 7'd31;
    assign thresholds[19] = 7'd51;
    assign thresholds[20] = 7'd17;
    assign thresholds[21] = 7'd42;
    assign thresholds[22] = 7'd25;
    assign thresholds[23] = 7'd32;
    assign thresholds[24] = 7'd29;
    assign thresholds[25] = 7'd35;
    assign thresholds[26] = 7'd25;
    assign thresholds[27] = 7'd53;
    assign thresholds[28] = 7'd38;
    assign thresholds[29] = 7'd33;
    assign thresholds[30] = 7'd37;
    assign thresholds[31] = 7'd44;
    assign thresholds[32] = 7'd52;
    assign thresholds[33] = 7'd59;
    assign thresholds[34] = 7'd31;
    assign thresholds[35] = 7'd23;
    assign thresholds[36] = 7'd26;
    assign thresholds[37] = 7'd36;
    assign thresholds[38] = 7'd37;
    assign thresholds[39] = 7'd18;
    assign thresholds[40] = 7'd30;
    assign thresholds[41] = 7'd32;
    assign thresholds[42] = 7'd35;
    assign thresholds[43] = 7'd28;
    assign thresholds[44] = 7'd34;
    assign thresholds[45] = 7'd48;
    assign thresholds[46] = 7'd34;
    assign thresholds[47] = 7'd31;
    assign thresholds[48] = 7'd54;
    assign thresholds[49] = 7'd29;
    assign thresholds[50] = 7'd0;
    assign thresholds[51] = 7'd39;
    assign thresholds[52] = 7'd32;
    assign thresholds[53] = 7'd35;
    assign thresholds[54] = 7'd64;
    assign thresholds[55] = 7'd26;
    assign thresholds[56] = 7'd35;
    assign thresholds[57] = 7'd19;
    assign thresholds[58] = 7'd35;
    assign thresholds[59] = 7'd27;
    assign thresholds[60] = 7'd32;
    assign thresholds[61] = 7'd0;
    assign thresholds[62] = 7'd30;
    assign thresholds[63] = 7'd31;


    // ============================================================
    // INTERMEDIATE SIGNALS
    // ============================================================

    wire [63:0] match_bits [0:63];

    wire [6:0] match_count [0:63];


    // ============================================================
    // 64 XNOR + POPCOUNT BLOCKS
    // ============================================================

    genvar n;

    generate

        for (n = 0; n < OUTPUT_COUNT; n = n + 1) begin : GEN_NEURONS

            xnor_popcount #(
                .WIDTH(INPUT_COUNT)
            ) xnor_popcount_inst (
                .inputs(inputs),
                .weights(weights[n]),
                .matches(match_bits[n]),
                .count(match_count[n])
            );


            // ====================================================
            // THRESHOLD + BINARY SIGN
            // ====================================================

            threshold_compare #(
                .COUNT_WIDTH(7)
            ) threshold_compare_inst (
                .count(match_count[n]),
                .threshold(thresholds[n]),
                .output_bit(outputs[n])
            );

        end

    endgenerate

endmodule
