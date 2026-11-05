
`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// Feature Register - Dual Bank
//
// Stores two independent 278-bit packet feature vectors.
//
// write_bank:
//   0 = write feature into bank 0
//   1 = write feature into bank 1
//
// read_bank:
//   0 = expose bank 0 on features
//   1 = expose bank 1 on features
//
// Feature mapping is unchanged from the original design.
//////////////////////////////////////////////////////////////////////////////////

module feature_register (
    input  wire         clk,
    input  wire         rst,

    // Feature write interface
    input  wire         load,
    input  wire [3:0]   feature_index,
    input  wire [26:0]  feature_in,
    input  wire         write_bank,

    // Bank read selection
    input  wire         read_bank,

    output wire [277:0] features
);

    // Two independent packet feature banks
    reg [277:0] feature_bank_0;
    reg [277:0] feature_bank_1;

    // Select which packet bank is visible to preprocessing
    assign features = read_bank ? feature_bank_1 : feature_bank_0;

    always @(posedge clk) begin
        if (rst) begin
            feature_bank_0 <= 278'd0;
            feature_bank_1 <= 278'd0;
        end
        else if (load) begin
            case (write_bank)

                1'b0: begin
                    case (feature_index)
                        4'd0:  feature_bank_0[13:0]    <= feature_in[13:0];
                        4'd1:  feature_bank_0[24:14]   <= feature_in[10:0];
                        4'd2:  feature_bank_0[49:25]   <= feature_in[24:0];
                        4'd3:  feature_bank_0[74:50]   <= feature_in[24:0];
                        4'd4:  feature_bank_0[90:75]   <= feature_in[15:0];
                        4'd5:  feature_bank_0[101:91]  <= feature_in[10:0];
                        4'd6:  feature_bank_0[102]     <= feature_in[0];
                        4'd7:  feature_bank_0[119:103] <= feature_in[16:0];
                        4'd8:  feature_bank_0[134:120] <= feature_in[14:0];
                        4'd9:  feature_bank_0[151:135] <= feature_in[16:0];
                        4'd10: feature_bank_0[172:152] <= feature_in[20:0];
                        4'd11: feature_bank_0[187:173] <= feature_in[14:0];
                        4'd12: feature_bank_0[208:188] <= feature_in[20:0];
                        4'd13: feature_bank_0[229:209] <= feature_in[20:0];
                        4'd14: feature_bank_0[256:230] <= feature_in[26:0];
                        4'd15: feature_bank_0[277:257] <= feature_in[20:0];
                        default: ;
                    endcase
                end

                1'b1: begin
                    case (feature_index)
                        4'd0:  feature_bank_1[13:0]    <= feature_in[13:0];
                        4'd1:  feature_bank_1[24:14]   <= feature_in[10:0];
                        4'd2:  feature_bank_1[49:25]   <= feature_in[24:0];
                        4'd3:  feature_bank_1[74:50]   <= feature_in[24:0];
                        4'd4:  feature_bank_1[90:75]   <= feature_in[15:0];
                        4'd5:  feature_bank_1[101:91]  <= feature_in[10:0];
                        4'd6:  feature_bank_1[102]     <= feature_in[0];
                        4'd7:  feature_bank_1[119:103] <= feature_in[16:0];
                        4'd8:  feature_bank_1[134:120] <= feature_in[14:0];
                        4'd9:  feature_bank_1[151:135] <= feature_in[16:0];
                        4'd10: feature_bank_1[172:152] <= feature_in[20:0];
                        4'd11: feature_bank_1[187:173] <= feature_in[14:0];
                        4'd12: feature_bank_1[208:188] <= feature_in[20:0];
                        4'd13: feature_bank_1[229:209] <= feature_in[20:0];
                        4'd14: feature_bank_1[256:230] <= feature_in[26:0];
                        4'd15: feature_bank_1[277:257] <= feature_in[20:0];
                        default: ;
                    endcase
                end

                default: ;
            endcase
        end
    end

endmodule
