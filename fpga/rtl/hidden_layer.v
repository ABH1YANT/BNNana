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
    //
    // Bit-reversed to match:
    //   weights[0]  -> input 0
    //   weights[1]  -> input 1
    //   ...
    //   weights[63] -> input 63
    //
    // 1 = +1
    // 0 = -1
    // ============================================================

    wire [63:0] weights [0:63];

    assign weights[0]  = 64'hDF641EB95367F1C0;
    assign weights[1]  = 64'hE8A23350F768D6A8;
    assign weights[2]  = 64'hCFF8553763743BC0;
    assign weights[3]  = 64'hEEFC885D0A3BB3C3;
    assign weights[4]  = 64'h2097BE4CD488C4BB;
    assign weights[5]  = 64'hC8227300F5E8D688;
    assign weights[6]  = 64'hCFE84CB5AA737945;
    assign weights[7]  = 64'hEFFC580F82E4AD46;
    assign weights[8]  = 64'h2CEF429E32AE4C2E;
    assign weights[9]  = 64'hCBC961B5CA7F6B46;
    assign weights[10] = 64'h10A7AA2A169A943A;
    assign weights[11] = 64'h229E6338D4C8D0A8;
    assign weights[12] = 64'h2007ABDA9C0984BE;
    assign weights[13] = 64'h133CF171EB50B1D0;
    assign weights[14] = 64'hCF7911B5E8647944;
    assign weights[15] = 64'hDF5C52A5CBF46B42;
    assign weights[16] = 64'h69A63333F8644404;
    assign weights[17] = 64'hCFE15895EB753B47;
    assign weights[18] = 64'h3219FFA74E0429FC;
    assign weights[19] = 64'h248B956AB48894BD;
    assign weights[20] = 64'hDF784835EA77F9C2;
    assign weights[21] = 64'hDF685025EA756947;
    assign weights[22] = 64'hCF7468B543777942;
    assign weights[23] = 64'h5396EF61D4C19281;
    assign weights[24] = 64'h5B06E16145C196E0;
    assign weights[25] = 64'hB704A169E171B7F0;
    assign weights[26] = 64'hFF5D051D42F76B42;
    assign weights[27] = 64'h20339D2A7C0896BC;
    assign weights[28] = 64'h300BBF28D48BD4BA;
    assign weights[29] = 64'h30C7A6CE5C9A46BB;
    assign weights[30] = 64'h3007A75A9C89D4BC;
    assign weights[31] = 64'hCF7870958BF76B42;
    assign weights[32] = 64'hCE5C4D356BFD6B43;
    assign weights[33] = 64'h2497D11A7C88D6B9;
    assign weights[34] = 64'h3092DF78BD8A14BC;
    assign weights[35] = 64'h100FB5127449D0B0;
    assign weights[36] = 64'hCFC841B162757B42;
    assign weights[37] = 64'hDF4D5AB7E3676B42;
    assign weights[38] = 64'hCFE514D54B7BED46;
    assign weights[39] = 64'hCFE841356A747BC3;
    assign weights[40] = 64'h23887FA6648429F4;
    assign weights[41] = 64'h685B188E16AF5E0F;
    assign weights[42] = 64'h4F8852154AF4BBC2;
    assign weights[43] = 64'hDFFD19B7C3752BC7;
    assign weights[44] = 64'h2013A7CABD8984BC;
    assign weights[45] = 64'h10E3AFC83488843F;
    assign weights[46] = 64'hFA06F961D55992A0;
    assign weights[47] = 64'h7B12EB61C561F6A0;
    assign weights[48] = 64'h3087AA6E748884BD;
    assign weights[49] = 64'hDB58493563F57B41;
    assign weights[50] = 64'hDDC541B383752146;
    assign weights[51] = 64'h22A7A3CA140894B8;
    assign weights[52] = 64'hEC4911DF02A7797C;
    assign weights[53] = 64'h30A7BAFA1C08D4BB;
    assign weights[54] = 64'h2087BCDA9C8216BC;
    assign weights[55] = 64'hDF7841A5E37D2946;
    assign weights[56] = 64'h30928758948806B8;
    assign weights[57] = 64'h20B287EEB58994B8;
    assign weights[58] = 64'h921CA769CB51B3D0;
    assign weights[59] = 64'hDF4D411543756BC6;
    assign weights[60] = 64'h208677ECD4D092A4;
    assign weights[61] = 64'h2087ACEAFC8886B8;
    assign weights[62] = 64'h4C5F5A9636AE4E2F;
    assign weights[63] = 64'hDF6C2EB1CB6F6F46;


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