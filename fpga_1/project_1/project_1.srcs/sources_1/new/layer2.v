`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/27/2026 12:32:27 PM
// Design Name: 
// Module Name: layer2
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

module layer2 #(
    parameter INPUT_COUNT  = 128,
    parameter OUTPUT_COUNT = 32
)(
    input  wire [INPUT_COUNT-1:0]  inputs,
    output wire [OUTPUT_COUNT-1:0] outputs
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
    // INTERMEDIATE SIGNALS
    // ============================================================

    wire [127:0] match_bits  [0:31];
    wire [7:0]   match_count [0:31];


    // ============================================================
    // 32 LAYER 2 NEURONS
    // ============================================================

    genvar n;

    generate

        for (n = 0; n < OUTPUT_COUNT; n = n + 1) begin : GEN_NEURONS

            // ----------------------------------------------------
            // Fixed-weight XNOR
            //
            // Since weights are constants:
            //
            // weight = 1 -> input
            // weight = 0 -> inverted input
            //
            // Synthesis can constant-fold this logic.
            // ----------------------------------------------------

            assign match_bits[n] = ~(inputs ^ weights[n]);


            // ----------------------------------------------------
            // 128-bit POPCOUNT
            //
            // Count range = 0..128
            // Therefore 8-bit count is required.
            // ----------------------------------------------------

            integer i;

            reg [7:0] count_temp;

            always @(*) begin

                count_temp = 8'd0;

                for (i = 0; i < INPUT_COUNT; i = i + 1) begin

                    count_temp =
                        count_temp
                        +
                        match_bits[n][i];

                end

            end

            assign match_count[n] = count_temp;


            // ----------------------------------------------------
            // BINARY SIGN / THRESHOLD
            //
            // count > threshold -> 1
            // count <= threshold -> 0
            // ----------------------------------------------------

            assign outputs[n] =
                (match_count[n] > thresholds[n]);

        end

    endgenerate

endmodule