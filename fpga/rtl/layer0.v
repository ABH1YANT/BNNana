`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company:
// Engineer:
//
// Create Date: 09/13/2026 11:49:35 PM
// Design Name:
// Module Name: layer0
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

module layer0 #(
    parameter INPUT_COUNT  = 16,
    parameter OUTPUT_COUNT = 64,
    parameter INPUT_WIDTH  = 8,
    parameter ACC_WIDTH    = 16
)(
    input wire [INPUT_COUNT*INPUT_WIDTH-1:0] inputs,

    output wire [OUTPUT_COUNT-1:0] outputs
);

    // ============================================================
    // LAYER 0 WEIGHTS
    //
    // Each 16-bit value contains the binary weights for one neuron.
    //
    // After reversing the exported Python bit ordering:
    //
    // bit 0  -> input 0
    // bit 1  -> input 1
    // ...
    // bit 15 -> input 15
    //
    // 1 = +1
    // 0 = -1
    // ============================================================

    wire [15:0] weights [0:63];

    assign weights[0]  = 16'hF420;
    assign weights[1]  = 16'h5C42;
    assign weights[2]  = 16'h3F9C;
    assign weights[3]  = 16'h2D4D;
    assign weights[4]  = 16'hC323;
    assign weights[5]  = 16'h27A9;
    assign weights[6]  = 16'h19BA;
    assign weights[7]  = 16'h72EF;
    assign weights[8]  = 16'h4D96;
    assign weights[9]  = 16'hF91F;
    assign weights[10] = 16'hABEF;
    assign weights[11] = 16'h9410;
    assign weights[12] = 16'hFFEB;
    assign weights[13] = 16'h5936;
    assign weights[14] = 16'h3BE7;
    assign weights[15] = 16'hD763;
    assign weights[16] = 16'hE2A3;
    assign weights[17] = 16'h1680;
    assign weights[18] = 16'hB498;
    assign weights[19] = 16'h3FEF;
    assign weights[20] = 16'h8F14;
    assign weights[21] = 16'h8956;
    assign weights[22] = 16'hDB76;
    assign weights[23] = 16'hBAAD;
    assign weights[24] = 16'h0CE3;
    assign weights[25] = 16'h2ECE;
    assign weights[26] = 16'h36CD;
    assign weights[27] = 16'h4F9C;
    assign weights[28] = 16'hA445;
    assign weights[29] = 16'hC2EF;
    assign weights[30] = 16'hC032;
    assign weights[31] = 16'hCDF3;
    assign weights[32] = 16'h3906;
    assign weights[33] = 16'h8410;
    assign weights[34] = 16'h768C;
    assign weights[35] = 16'hDC10;
    assign weights[36] = 16'hDFDC;
    assign weights[37] = 16'hF514;
    assign weights[38] = 16'hDBE3;
    assign weights[39] = 16'h1401;
    assign weights[40] = 16'hEA3B;
    assign weights[41] = 16'h3D1D;
    assign weights[42] = 16'hE29C;
    assign weights[43] = 16'h748D;
    assign weights[44] = 16'hBFE7;
    assign weights[45] = 16'hE3BF;
    assign weights[46] = 16'h3EAD;
    assign weights[47] = 16'hD2A3;
    assign weights[48] = 16'h308D;
    assign weights[49] = 16'hA445;
    assign weights[50] = 16'h9794;
    assign weights[51] = 16'h620C;
    assign weights[52] = 16'hD110;
    assign weights[53] = 16'hFFDC;
    assign weights[54] = 16'h1F04;
    assign weights[55] = 16'hEAEF;
    assign weights[56] = 16'h4C50;
    assign weights[57] = 16'hD510;
    assign weights[58] = 16'h4600;
    assign weights[59] = 16'h8BDE;
    assign weights[60] = 16'hF28C;
    assign weights[61] = 16'h0863;
    assign weights[62] = 16'h835E;
    assign weights[63] = 16'h0B4A;


    // ============================================================
    // LAYER 0 THRESHOLDS
    //
    // These are the exported BatchNorm-derived thresholds.
    //
    // They MUST remain 16-bit signed values.
    // ============================================================

    wire signed [15:0] thresholds [0:63];

    assign thresholds[0]  = 16'shF87F;
    assign thresholds[1]  = 16'shFF52;
    assign thresholds[2]  = 16'shFF4A;
    assign thresholds[3]  = 16'shFF4E;
    assign thresholds[4]  = 16'sh000C;
    assign thresholds[5]  = 16'shFF82;
    assign thresholds[6]  = 16'sh024B;
    assign thresholds[7]  = 16'sh00E6;
    assign thresholds[8]  = 16'sh0146;
    assign thresholds[9]  = 16'sh0011;
    assign thresholds[10] = 16'sh00D1;
    assign thresholds[11] = 16'shFFA4;
    assign thresholds[12] = 16'sh011F;
    assign thresholds[13] = 16'sh0260;
    assign thresholds[14] = 16'sh00B2;
    assign thresholds[15] = 16'sh0113;
    assign thresholds[16] = 16'shFF86;
    assign thresholds[17] = 16'shFD49;
    assign thresholds[18] = 16'shFF45;
    assign thresholds[19] = 16'sh0042;
    assign thresholds[20] = 16'shFF8D;
    assign thresholds[21] = 16'sh0076;
    assign thresholds[22] = 16'sh02C7;
    assign thresholds[23] = 16'shFFD5;
    assign thresholds[24] = 16'sh0019;
    assign thresholds[25] = 16'shFF90;
    assign thresholds[26] = 16'shFDE7;
    assign thresholds[27] = 16'sh0059;
    assign thresholds[28] = 16'shFDF0;
    assign thresholds[29] = 16'shFFFB;
    assign thresholds[30] = 16'sh0094;
    assign thresholds[31] = 16'sh0297;
    assign thresholds[32] = 16'shFF52;
    assign thresholds[33] = 16'shFF82;
    assign thresholds[34] = 16'shFDAE;
    assign thresholds[35] = 16'shFFCD;
    assign thresholds[36] = 16'sh001F;
    assign thresholds[37] = 16'sh003E;
    assign thresholds[38] = 16'sh012D;
    assign thresholds[39] = 16'shFD4A;
    assign thresholds[40] = 16'sh00C0;
    assign thresholds[41] = 16'sh013B;
    assign thresholds[42] = 16'shFFBA;
    assign thresholds[43] = 16'shFED7;
    assign thresholds[44] = 16'sh00F7;
    assign thresholds[45] = 16'sh00C7;
    assign thresholds[46] = 16'shFE56;
    assign thresholds[47] = 16'shFF7D;
    assign thresholds[48] = 16'shFD4A;
    assign thresholds[49] = 16'shFD83;
    assign thresholds[50] = 16'sh05E7;
    assign thresholds[51] = 16'shFDA7;
    assign thresholds[52] = 16'shFF77;
    assign thresholds[53] = 16'shFF03;
    assign thresholds[54] = 16'shFE88;
    assign thresholds[55] = 16'sh29A0;
    assign thresholds[56] = 16'sh014A;
    assign thresholds[57] = 16'sh0030;
    assign thresholds[58] = 16'shFDF3;
    assign thresholds[59] = 16'sh0002;
    assign thresholds[60] = 16'shFE71;
    assign thresholds[61] = 16'sh0019;
    assign thresholds[62] = 16'sh004D;
    assign thresholds[63] = 16'shFEED;


    // ============================================================
    // 64 BNN NEURONS
    // ============================================================

    genvar n;

    generate

        for (n = 0; n < OUTPUT_COUNT; n = n + 1) begin : GEN_NEURONS

            bnn_neuron #(
                .INPUT_COUNT(INPUT_COUNT),
                .INPUT_WIDTH(INPUT_WIDTH),
                .ACC_WIDTH(ACC_WIDTH)
            ) neuron_inst (

                .inputs(inputs),

                .weights(weights[n]),

                .threshold(thresholds[n]),

                .output_bit(outputs[n])

            );

        end

    endgenerate

endmodule