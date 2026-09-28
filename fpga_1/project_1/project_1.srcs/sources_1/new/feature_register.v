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

`timescale 1ns / 1ps

module feature_register (
    input  wire         clk,
    input  wire         rst,

    input  wire         load,
    input  wire [3:0]   feature_index,

    input  wire [26:0]  feature_in,

    output reg [277:0]  features
);

    always @(posedge clk) begin
        if (rst) begin
            features <= 278'd0;
        end
        else if (load) begin

            case (feature_index)

                4'd0:
                    features[13:0] <= feature_in[13:0];

                4'd1:
                    features[24:14] <= feature_in[10:0];

                4'd2:
                    features[49:25] <= feature_in[24:0];

                4'd3:
                    features[74:50] <= feature_in[24:0];

                4'd4:
                    features[90:75] <= feature_in[15:0];

                4'd5:
                    features[101:91] <= feature_in[10:0];

                4'd6:
                    features[102] <= feature_in[0];

                4'd7:
                    features[119:103] <= feature_in[16:0];

                4'd8:
                    features[134:120] <= feature_in[14:0];

                4'd9:
                    features[151:135] <= feature_in[16:0];

                4'd10:
                    features[172:152] <= feature_in[20:0];

                4'd11:
                    features[187:173] <= feature_in[14:0];

                4'd12:
                    features[208:188] <= feature_in[20:0];

                4'd13:
                    features[229:209] <= feature_in[20:0];

                4'd14:
                    features[256:230] <= feature_in[26:0];

                4'd15:
                    features[277:257] <= feature_in[20:0];

                default:
                    features <= features;

            endcase
        end
    end

endmodule