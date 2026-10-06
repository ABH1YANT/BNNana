`timescale 1ns / 1ps

module preprocessing (
    input  wire         clk,
    input  wire [277:0] features,
    output wire [127:0] preprocessed
);

    // ============================================================
    // Feature fields
    // ============================================================

    wire [13:0] feature_0;
    wire [10:0] feature_1;
    wire [24:0] feature_2;
    wire [24:0] feature_3;
    wire [15:0] feature_4;
    wire [10:0] feature_5;
    wire        feature_6;
    wire [16:0] feature_7;
    wire [14:0] feature_8;
    wire [16:0] feature_9;
    wire [20:0] feature_10;
    wire [14:0] feature_11;
    wire [20:0] feature_12;
    wire [20:0] feature_13;
    wire [26:0] feature_14;
    wire [20:0] feature_15;

    assign feature_0  = features[13:0];
    assign feature_1  = features[24:14];
    assign feature_2  = features[49:25];
    assign feature_3  = features[74:50];
    assign feature_4  = features[90:75];
    assign feature_5  = features[101:91];
    assign feature_6  = features[102];
    assign feature_7  = features[119:103];
    assign feature_8  = features[134:120];
    assign feature_9  = features[151:135];
    assign feature_10 = features[172:152];
    assign feature_11 = features[187:173];
    assign feature_12 = features[208:188];
    assign feature_13 = features[229:209];
    assign feature_14 = features[256:230];
    assign feature_15 = features[277:257];


    // ============================================================
    // BRAM address generation
    // ============================================================

    wire [11:0] addr_0;
    wire [9:0]  addr_1;
    wire [15:0] addr_2;
    wire [15:0] addr_3;
    wire [11:0] addr_4;
    wire [9:0]  addr_5;
    wire [0:0]  addr_6;
    wire [11:0] addr_7;
    wire [11:0] addr_8;
    wire [11:0] addr_9;
    wire [15:0] addr_10;
    wire [11:0] addr_11;
    wire [15:0] addr_12;
    wire [15:0] addr_13;
    wire [15:0] addr_14;
    wire [15:0] addr_15;

    assign addr_0  = feature_0[13:2];
    assign addr_1  = feature_1[10:1];
    assign addr_2  = feature_2[24:9];
    assign addr_3  = feature_3[24:9];
    assign addr_4  = feature_4[15:4];
    assign addr_5  = feature_5[10:1];
    assign addr_6  = feature_6;
    assign addr_7  = feature_7[16:5];
    assign addr_8  = feature_8[14:3];
    assign addr_9  = feature_9[16:5];
    assign addr_10 = feature_10[20:5];
    assign addr_11 = feature_11[14:3];
    assign addr_12 = feature_12[20:5];
    assign addr_13 = feature_13[20:5];
    assign addr_14 = feature_14[26:11];
    assign addr_15 = feature_15[20:5];


    // ============================================================
    // BRAM LUTs
    // ============================================================

    (* rom_style = "block" *)
    reg [7:0] lut_0 [0:4095];

    (* rom_style = "block" *)
    reg [7:0] lut_1 [0:1023];

    (* rom_style = "block" *)
    reg [7:0] lut_2 [0:65535];

    (* rom_style = "block" *)
    reg [7:0] lut_3 [0:65535];

    (* rom_style = "block" *)
    reg [7:0] lut_4 [0:4095];

    (* rom_style = "block" *)
    reg [7:0] lut_5 [0:1023];

    (* rom_style = "block" *)
    reg [7:0] lut_6 [0:1];

    (* rom_style = "block" *)
    reg [7:0] lut_7 [0:4095];

    (* rom_style = "block" *)
    reg [7:0] lut_8 [0:4095];

    (* rom_style = "block" *)
    reg [7:0] lut_9 [0:4095];

    (* rom_style = "block" *)
    reg [7:0] lut_10 [0:65535];

    (* rom_style = "block" *)
    reg [7:0] lut_11 [0:4095];

    (* rom_style = "block" *)
    reg [7:0] lut_12 [0:65535];

    (* rom_style = "block" *)
    reg [7:0] lut_13 [0:65535];

    (* rom_style = "block" *)
    reg [7:0] lut_14 [0:65535];

    (* rom_style = "block" *)
    reg [7:0] lut_15 [0:65535];


    // ============================================================
    // Load LUT contents
    // ============================================================

    initial begin
        $readmemh("Bwd_Packet_Length_Max.mem",       lut_0);
        $readmemh("Min_Packet_Length.mem",            lut_1);
        $readmemh("Subflow_Bwd_Bytes.mem",            lut_2);
        $readmemh("Total_Length_of_Bwd_Packets.mem",  lut_3);
        $readmemh("Destination_Port.mem",             lut_4);
        $readmemh("min_seg_size_forward.mem",         lut_5);
        $readmemh("ACK_Flag_Count.mem",               lut_6);
        $readmemh("Subflow_Bwd_Packets.mem",          lut_7);
        $readmemh("Fwd_Packet_Length_Max.mem",        lut_8);
        $readmemh("Total_Backward_Packets.mem",       lut_9);
        $readmemh("Subflow_Fwd_Bytes.mem",            lut_10);
        $readmemh("Max_Packet_Length.mem",             lut_11);
        $readmemh("Total_Length_of_Fwd_Packets.mem",  lut_12);
        $readmemh("Bwd_Header_Length.mem",             lut_13);
        $readmemh("Flow_Duration.mem",                 lut_14);
        $readmemh("Fwd_Header_Length.mem",             lut_15);
    end


    // ============================================================
    // BRAM output registers
    // ============================================================

    reg [7:0] q0;
    reg [7:0] q1;
    reg [7:0] q2;
    reg [7:0] q3;
    reg [7:0] q4;
    reg [7:0] q5;
    reg [7:0] q6;
    reg [7:0] q7;
    reg [7:0] q8;
    reg [7:0] q9;
    reg [7:0] q10;
    reg [7:0] q11;
    reg [7:0] q12;
    reg [7:0] q13;
    reg [7:0] q14;
    reg [7:0] q15;


    // ============================================================
    // SECOND OUTPUT REGISTER
    //
    // This is the important new pipeline boundary.
    //
    // BRAM -> q registers -> output registers -> Layer0
    // ============================================================

    (* DONT_TOUCH = "TRUE" *)
    reg [127:0] preprocessed_reg;


    // ============================================================
    // BRAM lookup
    // ============================================================

    always @(posedge clk) begin

        q0  <= lut_0[addr_0];
        q1  <= lut_1[addr_1];
        q2  <= lut_2[addr_2];
        q3  <= lut_3[addr_3];
        q4  <= lut_4[addr_4];
        q5  <= lut_5[addr_5];
        q6  <= lut_6[addr_6];
        q7  <= lut_7[addr_7];
        q8  <= lut_8[addr_8];
        q9  <= lut_9[addr_9];
        q10 <= lut_10[addr_10];
        q11 <= lut_11[addr_11];
        q12 <= lut_12[addr_12];
        q13 <= lut_13[addr_13];
        q14 <= lut_14[addr_14];
        q15 <= lut_15[addr_15];

    end


    // ============================================================
    // Extra pipeline register
    // ============================================================

    always @(posedge clk) begin

        preprocessed_reg <= {
            q15,
            q14,
            q13,
            q12,
            q11,
            q10,
            q9,
            q8,
            q7,
            q6,
            q5,
            q4,
            q3,
            q2,
            q1,
            q0
        };

    end


    // ============================================================
    // Preprocessed output
    // ============================================================

    assign preprocessed = preprocessed_reg;

endmodule