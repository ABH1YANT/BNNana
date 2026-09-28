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
// 
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
    // bit 0  -> input 0
    // bit 1  -> input 1
    // ...
    // bit 15 -> input 15
    //
    // 1 = +1
    // 0 = -1
    // ============================================================

    wire [15:0] weights [0:63];

    assign weights[0]  = 16'h042F;
    assign weights[1]  = 16'h423A;
    assign weights[2]  = 16'h39FC;
    assign weights[3]  = 16'hB2B4;
    assign weights[4]  = 16'hC4C3;
    assign weights[5]  = 16'h95E4;
    assign weights[6]  = 16'h5D98;
    assign weights[7]  = 16'hF74E;
    assign weights[8]  = 16'h69B2;
    assign weights[9]  = 16'hF89F;
    assign weights[10] = 16'hF7D5;
    assign weights[11] = 16'h0829;
    assign weights[12] = 16'hD7FF;
    assign weights[13] = 16'h6C9A;
    assign weights[14] = 16'hE7DC;
    assign weights[15] = 16'hC6EB;
    assign weights[16] = 16'hC547;
    assign weights[17] = 16'h0168;
    assign weights[18] = 16'h192D;
    assign weights[19] = 16'hF7FC;
    assign weights[20] = 16'h28F1;
    assign weights[21] = 16'h6A91;
    assign weights[22] = 16'h6EDB;
    assign weights[23] = 16'hB55D;
    assign weights[24] = 16'hC730;
    assign weights[25] = 16'h7374;
    assign weights[26] = 16'hB36C;
    assign weights[27] = 16'h39F2;
    assign weights[28] = 16'hA225;
    assign weights[29] = 16'hF743;
    assign weights[30] = 16'h4C03;
    assign weights[31] = 16'hCFB3;
    assign weights[32] = 16'h609C;
    assign weights[33] = 16'h0821;
    assign weights[34] = 16'h316E;
    assign weights[35] = 16'h083B;
    assign weights[36] = 16'h3BFB;
    assign weights[37] = 16'h28AF;
    assign weights[38] = 16'hC7DB;
    assign weights[39] = 16'h8028;
    assign weights[40] = 16'hDC57;
    assign weights[41] = 16'hB8BC;
    assign weights[42] = 16'h3947;
    assign weights[43] = 16'hB12E;
    assign weights[44] = 16'hE7FD;
    assign weights[45] = 16'hFDC7;
    assign weights[46] = 16'hB57C;
    assign weights[47] = 16'hC54B;
    assign weights[48] = 16'hB10C;
    assign weights[49] = 16'hA225;
    assign weights[50] = 16'h29E9;
    assign weights[51] = 16'h3046;
    assign weights[52] = 16'h088B;
    assign weights[53] = 16'h3BFF;
    assign weights[54] = 16'h20F8;
    assign weights[55] = 16'hF757;
    assign weights[56] = 16'h0A32;
    assign weights[57] = 16'h08AB;
    assign weights[58] = 16'h0062;
    assign weights[59] = 16'h7BD1;
    assign weights[60] = 16'h314F;
    assign weights[61] = 16'hC610;
    assign weights[62] = 16'h7AC1;
    assign weights[63] = 16'h52D0;


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
