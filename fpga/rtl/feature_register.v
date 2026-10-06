`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/13/2026 04:04:24 PM
// Design Name: 
// Module Name: feature_register
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

//////////////////////////////////////////////////////////////////////////////////
// Feature Register
//
// Stores the 16 selected FPGA features in the exact order used by:
//   selected_features.json
//
// Feature layout inside the 278-bit feature bus:
//
//   [13:0]     Feature 0  - Bwd Packet Length Max       - 14 bits
//   [24:14]    Feature 1  - Min Packet Length           - 11 bits
//   [49:25]    Feature 2  - Subflow Bwd Bytes           - 25 bits
//   [74:50]    Feature 3  - Total Length Bwd Packets    - 25 bits
//   [90:75]    Feature 4  - Destination Port            - 16 bits
//   [101:91]   Feature 5  - min_seg_size_forward        - 11 bits
//   [102]       Feature 6  - ACK Flag Count              - 1 bit
//   [119:103]  Feature 7  - Subflow Bwd Packets          - 17 bits
//   [134:120]  Feature 8  - Fwd Packet Length Max       - 15 bits
//   [151:135]  Feature 9  - Total Backward Packets       - 17 bits
//   [172:152]  Feature 10 - Subflow Fwd Bytes            - 21 bits
//   [187:173]  Feature 11 - Max Packet Length            - 15 bits
//   [208:188]  Feature 12 - Total Length Fwd Packets     - 21 bits
//   [229:209]  Feature 13 - Bwd Header Length            - 21 bits
//   [256:230]  Feature 14 - Flow Duration                - 27 bits
//   [277:257]  Feature 15 - Fwd Header Length            - 21 bits
//
//////////////////////////////////////////////////////////////////////////////////

module feature_register (
    input  wire        clk,
    input  wire        rst,

    input  wire        load,
    input  wire [3:0]  feature_index,
    input  wire [26:0] feature_in,

    output reg [277:0] features
);

    always @(posedge clk) begin

        if (rst) begin

            features <= 278'd0;

        end
        else if (load) begin

            case (feature_index)

                // ----------------------------------------------------
                // Feature 0
                // Bwd Packet Length Max
                // 14 bits
                // ----------------------------------------------------
                4'd0:
                    features[13:0] <= feature_in[13:0];


                // ----------------------------------------------------
                // Feature 1
                // Min Packet Length
                // 11 bits
                // ----------------------------------------------------
                4'd1:
                    features[24:14] <= feature_in[10:0];


                // ----------------------------------------------------
                // Feature 2
                // Subflow Bwd Bytes
                // 25 bits
                // ----------------------------------------------------
                4'd2:
                    features[49:25] <= feature_in[24:0];


                // ----------------------------------------------------
                // Feature 3
                // Total Length of Bwd Packets
                // 25 bits
                // ----------------------------------------------------
                4'd3:
                    features[74:50] <= feature_in[24:0];


                // ----------------------------------------------------
                // Feature 4
                // Destination Port
                // 16 bits
                // ----------------------------------------------------
                4'd4:
                    features[90:75] <= feature_in[15:0];


                // ----------------------------------------------------
                // Feature 5
                // min_seg_size_forward
                // 11 bits
                // ----------------------------------------------------
                4'd5:
                    features[101:91] <= feature_in[10:0];


                // ----------------------------------------------------
                // Feature 6
                // ACK Flag Count
                // 1 bit
                // ----------------------------------------------------
                4'd6:
                    features[102] <= feature_in[0];


                // ----------------------------------------------------
                // Feature 7
                // Subflow Bwd Packets
                // 17 bits
                // ----------------------------------------------------
                4'd7:
                    features[119:103] <= feature_in[16:0];


                // ----------------------------------------------------
                // Feature 8
                // Fwd Packet Length Max
                // 15 bits
                // ----------------------------------------------------
                4'd8:
                    features[134:120] <= feature_in[14:0];


                // ----------------------------------------------------
                // Feature 9
                // Total Backward Packets
                // 17 bits
                // ----------------------------------------------------
                4'd9:
                    features[151:135] <= feature_in[16:0];


                // ----------------------------------------------------
                // Feature 10
                // Subflow Fwd Bytes
                // 21 bits
                // ----------------------------------------------------
                4'd10:
                    features[172:152] <= feature_in[20:0];


                // ----------------------------------------------------
                // Feature 11
                // Max Packet Length
                // 15 bits
                // ----------------------------------------------------
                4'd11:
                    features[187:173] <= feature_in[14:0];


                // ----------------------------------------------------
                // Feature 12
                // Total Length of Fwd Packets
                // 21 bits
                // ----------------------------------------------------
                4'd12:
                    features[208:188] <= feature_in[20:0];


                // ----------------------------------------------------
                // Feature 13
                // Bwd Header Length
                // 21 bits
                // ----------------------------------------------------
                4'd13:
                    features[229:209] <= feature_in[20:0];


                // ----------------------------------------------------
                // Feature 14
                // Flow Duration
                // 27 bits
                // ----------------------------------------------------
                4'd14:
                    features[256:230] <= feature_in[26:0];


                // ----------------------------------------------------
                // Feature 15
                // Fwd Header Length
                // 21 bits
                // ----------------------------------------------------
                4'd15:
                    features[277:257] <= feature_in[20:0];


                default:
                    features <= features;

            endcase

        end

    end

endmodule