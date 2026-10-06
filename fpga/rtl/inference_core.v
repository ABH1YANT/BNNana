`timescale 1ns / 1ps

module inference_core (
    input wire         clk,
    input wire         rst,
    input wire         start,
    input wire [127:0] features,

    output wire        classification,
    output reg         inference_done,
    output reg         busy
);

    // ============================================================
    // Pipeline registers
    // ============================================================

    // Stage 0: capture preprocessed input
    (* DONT_TOUCH = "TRUE" *)
    reg [127:0] preprocessed_reg;

    // Stage 1: Layer 0 output
    reg [63:0] layer0_reg;

    // Stage 2: Layer 1 output
    reg [63:0] layer1_reg;

    // Stage 3: Layer 2 output
    reg [31:0] layer2_reg;

    // Final result
    reg classification_reg;


    // ============================================================
    // Combinational layer outputs
    // ============================================================

    wire [63:0]  layer0_comb;
    wire [63:0]  layer1_comb;
    wire [127:0] layer2_input;
    wire [31:0]  layer2_comb;
    wire [159:0] output_input;
    wire         output_comb;


    // ============================================================
    // Bit-order conversion
    //
    // Python exports binary vectors MSB-first.
    //
    // RTL layer registers store the corresponding first Python
    // bit at bit 0.
    //
    // Therefore each 64-bit activation vector must be reversed
    // before being presented to the next Python-exported weight
    // matrix.
    // ============================================================

    function [63:0] reverse64;
        input [63:0] value;
        integer k;

        begin
            for (k = 0; k < 64; k = k + 1) begin
                reverse64[k] = value[63-k];
            end
        end
    endfunction

    wire [63:0] layer0_for_layer2;
    wire [63:0] layer1_for_layer2;

    assign layer0_for_layer2 = reverse64(layer0_reg);
    assign layer1_for_layer2 = reverse64(layer1_reg);


    // ============================================================
    // Layer 0
    // ============================================================

    layer0 layer0_inst (
        .inputs(preprocessed_reg),
        .outputs(layer0_comb)
    );


    // ============================================================
    // Layer 1
    // ============================================================

    hidden_layer hidden_layer_inst (
        .inputs(layer0_reg),
        .outputs(layer1_comb)
    );


    // ============================================================
    // Layer 2
    //
    // Python architecture:
    //
    //     Layer 2 input = [Layer 0 output | Layer 1 output]
    //
    // Each 64-bit activation vector is reversed here so that
    // the Python-exported weight bit ordering is preserved.
    // ============================================================

    assign layer2_input = {
        layer0_for_layer2,
        layer1_for_layer2
    };

    layer2 layer2_inst (
        .inputs(layer2_input),
        .outputs(layer2_comb)
    );


    // ============================================================
    // Output layer
    //
    // NOT being debugged/modified yet.
    //
    // We will verify Layer 2 first.
    // ============================================================

    assign output_input = {
        layer0_reg,
        layer1_reg,
        layer2_reg
    };

    output_layer output_layer_inst (
        .inputs(output_input),
        .output_bit(output_comb)
    );


    // ============================================================
    // Pipeline control
    // ============================================================

    localparam STAGE_IDLE   = 3'd0;
    localparam STAGE_L0     = 3'd1;
    localparam STAGE_L1     = 3'd2;
    localparam STAGE_L2     = 3'd3;
    localparam STAGE_OUTPUT = 3'd4;

    reg [2:0] stage;
    reg       start_seen;


    // ============================================================
    // Sequential pipeline
    // ============================================================

    always @(posedge clk) begin

        if (rst) begin

            preprocessed_reg <= 128'd0;
            layer0_reg       <= 64'd0;
            layer1_reg       <= 64'd0;
            layer2_reg       <= 32'd0;

            classification_reg <= 1'b0;

            stage          <= STAGE_IDLE;
            start_seen     <= 1'b0;
            busy           <= 1'b0;
            inference_done <= 1'b0;

        end
        else begin

            // Default: done is a one-cycle pulse
            inference_done <= 1'b0;


            // Allow a new start after start has been released
            if (!start)
                start_seen <= 1'b0;


            // ----------------------------------------------------
            // Stage 0
            // Capture preprocessing result
            // ----------------------------------------------------

            if (start && !start_seen && !busy) begin

                preprocessed_reg <= features;

                busy       <= 1'b1;
                start_seen <= 1'b1;

                stage <= STAGE_L0;
            end


            // ----------------------------------------------------
            // Stage 1
            // Layer 0 computation
            // ----------------------------------------------------

            else if (busy && stage == STAGE_L0) begin

                layer0_reg <= layer0_comb;

                stage <= STAGE_L1;
            end


            // ----------------------------------------------------
            // Stage 2
            // Layer 1 computation
            // ----------------------------------------------------

            else if (busy && stage == STAGE_L1) begin

                layer1_reg <= layer1_comb;

                stage <= STAGE_L2;
            end


            // ----------------------------------------------------
            // Stage 3
            // Layer 2 computation
            // ----------------------------------------------------

            else if (busy && stage == STAGE_L2) begin

                layer2_reg <= layer2_comb;

                stage <= STAGE_OUTPUT;
            end


            // ----------------------------------------------------
            // Stage 4
            // Final output computation
            // ----------------------------------------------------

            else if (busy && stage == STAGE_OUTPUT) begin

                classification_reg <= output_comb;

                busy           <= 1'b0;
                inference_done <= 1'b1;

                stage <= STAGE_IDLE;
            end

        end

    end


    // ============================================================
    // Final classification output
    // ============================================================

    assign classification = classification_reg;

endmodule