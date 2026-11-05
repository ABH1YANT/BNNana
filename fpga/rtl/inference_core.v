`timescale 1ns / 1ps

module inference_core (
    input wire         clk,
    input wire         rst,
    input wire         start,
    input wire [127:0] features,

    output wire        classification,
    output wire        inference_done,
    output wire        busy,

    output wire [2:0]  debug_stage,
    output wire [31:0] input_layer_cycles,
    output wire [31:0] hidden_layer_1_cycles,
    output wire [31:0] hidden_layer_2_cycles,
    output wire [31:0] output_layer_cycles,
    output wire [31:0] inference_cycle_count,
    output wire [31:0] total_inference_cycles
);

    // ============================================================
    // LAYER OUTPUTS AND VALID SIGNALS
    // ============================================================

    wire [63:0] l0_outputs;
    wire        l0_done;

    wire [63:0] h1_outputs;
    wire        h1_done;

    wire [31:0] h2_outputs;
    wire        h2_done;

    wire        final_output;
    wire        final_done;


    // ============================================================
    // BIT ORDER CONVERSION
    // ============================================================

    function [63:0] reverse64;
        input [63:0] value;
        integer k;
        begin
            for (k = 0; k < 64; k = k + 1)
                reverse64[k] = value[63-k];
        end
    endfunction


    // ============================================================
    // SKIP CONNECTION DELAY 1
    //
    // Delay Layer 0 output by four cycles to align it
    // with Hidden Layer 1 output.
    // ============================================================

    reg [63:0] l0_delay [0:3];

    wire [127:0] h2_input;

    assign h2_input = {
        h1_outputs,
        l0_delay[3]
    };


    // ============================================================
    // SKIP CONNECTION DELAY 2
    //
    // Delay Layer 0 and Layer 1 outputs by nine cycles
    // to align them with Hidden Layer 2 output.
    // ============================================================

    reg [127:0] skip_delay [0:8];

    wire [159:0] output_input;

    assign output_input = {
        skip_delay[8],
        h2_outputs
    };


    // ============================================================
    // LAYER 0: INPUT LAYER
    //
    // Accepts one new feature vector whenever start is high.
    // ============================================================

    input_layer input_layer_inst (
        .clk     (clk),
        .rst     (rst),
        .enable  (start),
        .inputs  (features),
        .outputs (l0_outputs),
        .done    (l0_done)
    );


    // ============================================================
    // LAYER 1: HIDDEN LAYER 1
    //
    // Starts whenever Layer 0 produces a valid result.
    // ============================================================

    hidden_layer_1 hidden_layer_1_inst (
        .clk     (clk),
        .rst     (rst),
        .enable  (l0_done),
        .inputs  (l0_outputs),
        .outputs (h1_outputs),
        .done    (h1_done)
    );


    // ============================================================
    // LAYER 2: HIDDEN LAYER 2
    //
    // Combines the aligned Layer 0 and Layer 1 outputs.
    // ============================================================

    hidden_layer_2 hidden_layer_2_inst (
        .clk     (clk),
        .rst     (rst),
        .start   (h1_done),
        .inputs  (h2_input),
        .outputs (h2_outputs),
        .done    (h2_done)
    );


    // ============================================================
    // OUTPUT LAYER
    //
    // Combines the two delayed skip connections with
    // the Hidden Layer 2 output.
    // ============================================================

    output_layer output_layer_inst (
        .clk        (clk),
        .rst        (rst),
        .enable     (h2_done),
        .inputs     (output_input),
        .output_bit (final_output),
        .done       (final_done)
    );


    // ============================================================
    // FINAL OUTPUTS
    // ============================================================

    assign classification = final_output;
    assign inference_done = final_done;


    // ============================================================
    // OUTSTANDING INFERENCE COUNTER
    //
    // Supports multiple simultaneous inferences.
    // ============================================================

    reg [31:0] outstanding_count;

    assign busy = (outstanding_count != 0);


    // ============================================================
    // DEBUG REGISTERS
    // ============================================================

    reg [2:0] stage;

    reg [31:0] input_layer_cycles_reg;
    reg [31:0] hidden_layer_1_cycles_reg;
    reg [31:0] hidden_layer_2_cycles_reg;
    reg [31:0] output_layer_cycles_reg;

    reg [31:0] inference_cycle_count_reg;
    reg [31:0] total_inference_cycles_reg;

    assign debug_stage = stage;

    assign input_layer_cycles = input_layer_cycles_reg;
    assign hidden_layer_1_cycles = hidden_layer_1_cycles_reg;
    assign hidden_layer_2_cycles = hidden_layer_2_cycles_reg;
    assign output_layer_cycles = output_layer_cycles_reg;

    assign inference_cycle_count = inference_cycle_count_reg;
    assign total_inference_cycles = total_inference_cycles_reg;

    localparam PIPELINE_LATENCY = 32'd25;


    // ============================================================
    // PIPELINE DATA ALIGNMENT AND DEBUG CONTROL
    // ============================================================

    integer d;

    always @(posedge clk) begin

        if (rst) begin

            // Layer 0 alignment registers
            for (d = 0; d < 4; d = d + 1)
                l0_delay[d] <= 64'd0;

            // Skip connection alignment registers
            for (d = 0; d < 9; d = d + 1)
                skip_delay[d] <= 128'd0;

            // Outstanding inference tracking
            outstanding_count <= 32'd0;

            // Debug stage
            stage <= 3'd0;

            // Debug counters
            input_layer_cycles_reg <= 32'd0;
            hidden_layer_1_cycles_reg <= 32'd0;
            hidden_layer_2_cycles_reg <= 32'd0;
            output_layer_cycles_reg <= 32'd0;

            inference_cycle_count_reg <= 32'd0;
            total_inference_cycles_reg <= 32'd0;

        end

        else begin

            // ----------------------------------------------------
            // LAYER 0 -> LAYER 1 ALIGNMENT
            // ----------------------------------------------------

            if (l0_done)
                l0_delay[0] <= l0_outputs;
            else
                l0_delay[0] <= 64'd0;

            for (d = 1; d < 4; d = d + 1)
                l0_delay[d] <= l0_delay[d-1];


            // ----------------------------------------------------
            // LAYER 1 -> OUTPUT SKIP CONNECTION ALIGNMENT
            // ----------------------------------------------------

            if (h1_done)
                skip_delay[0] <= {
                    l0_delay[3],
                    h1_outputs
                };
            else
                skip_delay[0] <= 128'd0;

            for (d = 1; d < 9; d = d + 1)
                skip_delay[d] <= skip_delay[d-1];


            // ----------------------------------------------------
            // OUTSTANDING INFERENCE TRACKING
            // ----------------------------------------------------

            case ({start, final_done})

                2'b10:
                    outstanding_count <= outstanding_count + 1'b1;

                2'b01: begin
                    if (outstanding_count != 0)
                        outstanding_count <= outstanding_count - 1'b1;
                end

                default:
                    outstanding_count <= outstanding_count;

            endcase


            // ----------------------------------------------------
            // DEBUG COUNTERS
            // ----------------------------------------------------

            if (start)
                input_layer_cycles_reg <=
                    input_layer_cycles_reg + 1'b1;

            if (l0_done)
                hidden_layer_1_cycles_reg <=
                    hidden_layer_1_cycles_reg + 1'b1;

            if (h1_done)
                hidden_layer_2_cycles_reg <=
                    hidden_layer_2_cycles_reg + 1'b1;

            if (h2_done)
                output_layer_cycles_reg <=
                    output_layer_cycles_reg + 1'b1;

            if (busy || start)
                inference_cycle_count_reg <=
                    inference_cycle_count_reg + 1'b1;

            if (final_done)
                total_inference_cycles_reg <=
                    total_inference_cycles_reg + PIPELINE_LATENCY;


            // ----------------------------------------------------
            // DEBUG STAGE
            // ----------------------------------------------------

            if (final_done)
                stage <= 3'd0;
            else if (h2_done)
                stage <= 3'd4;
            else if (h1_done)
                stage <= 3'd3;
            else if (l0_done)
                stage <= 3'd2;
            else if (start)
                stage <= 3'd1;

        end
    end

endmodule
