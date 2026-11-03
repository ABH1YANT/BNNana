`timescale 1ns / 1ps

module inference_core (
    input wire         clk,
    input wire         rst,
    input wire         start,
    input wire [127:0] features,

    output wire        classification,
    output reg         inference_done,
    output reg         busy,

    // Debug outputs for ILA
    output wire [2:0]  debug_stage,
    output wire [31:0] input_layer_cycles,
    output wire [31:0] hidden_layer_1_cycles,
    output wire [31:0] hidden_layer_2_cycles,
    output wire [31:0] output_layer_cycles,
    output wire [31:0] inference_cycle_count,
    output wire [31:0] total_inference_cycles
);

    // ============================================================
    // Pipeline registers
    // ============================================================

    // Stage 0: capture preprocessed input
    (* DONT_TOUCH = "TRUE" *)
    reg [127:0] preprocessed_reg;

    // Stage 1: Layer 0 output
    reg [63:0] input_layer_reg;

    // Stage 2: Layer 1 output
    reg [63:0] hidden_layer_1_reg;

    // Stage 3: Layer 2 output
    reg [31:0] hidden_layer_2_reg;

    // Final result
    reg classification_reg;

    reg [2:0] stage;
    reg       start_seen;

    // ============================================================
    // DEBUG CYCLE COUNTERS
    // ============================================================

    (* MARK_DEBUG = "TRUE" *)
    reg [31:0] input_layer_cycles_reg;

    (* MARK_DEBUG = "TRUE" *)
    reg [31:0] hidden_layer_1_cycles_reg;

    (* MARK_DEBUG = "TRUE" *)
    reg [31:0] hidden_layer_2_cycles_reg;

    (* MARK_DEBUG = "TRUE" *)
    reg [31:0] output_layer_cycles_reg;

    (* MARK_DEBUG = "TRUE" *)
    reg [31:0] inference_cycle_count_reg;

    (* MARK_DEBUG = "TRUE" *)
    reg [31:0] total_inference_cycles_reg;


    // Expose the existing stage register
    assign debug_stage = stage;


    // Connect internal counters to module outputs
    assign input_layer_cycles = input_layer_cycles_reg;

    assign hidden_layer_1_cycles = hidden_layer_1_cycles_reg;

    assign hidden_layer_2_cycles = hidden_layer_2_cycles_reg;

    assign output_layer_cycles = output_layer_cycles_reg;

    assign inference_cycle_count = inference_cycle_count_reg;

    assign total_inference_cycles = total_inference_cycles_reg;

    // ============================================================
    // Combinational layer outputs
    // ============================================================

    wire [63:0]  input_layer_comb;
    wire [63:0]  hidden_layer_1_comb;
    wire [127:0] hidden_layer_2_input;
    wire [31:0]  hidden_layer_2_comb;
    wire [159:0] output_input;
    wire         output_comb;
    wire hidden_layer_2_done;
    reg  hidden_layer_2_start;


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

    wire [63:0] input_layer_for_hidden_layer_2;
    wire [63:0] hidden_layer_1_for_hidden_layer_2;

    assign input_layer_for_hidden_layer_2 = reverse64(input_layer_reg);
    assign hidden_layer_1_for_hidden_layer_2 = reverse64(hidden_layer_1_reg);


    // ============================================================
    // Layer 0
    // ============================================================

    input_layer input_layer_inst (
        .inputs(preprocessed_reg),
        .outputs(input_layer_comb)
    );


    // ============================================================
    // Layer 1
    // ============================================================

    hidden_layer_1 hidden_layer_1_inst (
        .inputs(input_layer_reg),
        .outputs(hidden_layer_1_comb)
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

    assign hidden_layer_2_input = {
        input_layer_for_hidden_layer_2,
        hidden_layer_1_for_hidden_layer_2
    };

    hidden_layer_2 hidden_layer_2_inst (
        .clk     (clk),
        .rst     (rst),
        .start   (hidden_layer_2_start),
        .inputs  (hidden_layer_2_input),
        .outputs(hidden_layer_2_comb),
        .done    (hidden_layer_2_done)
    );


    // ============================================================
    // Output layer
    //
    // NOT being debugged/modified yet.
    //
    // We will verify Layer 2 first.
    // ============================================================

    assign output_input = {
        input_layer_reg,
        hidden_layer_1_reg,
        hidden_layer_2_reg
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


    // ============================================================
    // SEQUENTIAL PIPELINE + DEBUG CYCLE COUNTERS
    // ============================================================

        
    always @(posedge clk) begin

        if (rst) begin

            preprocessed_reg    <= 128'd0;
            input_layer_reg     <= 64'd0;
            hidden_layer_1_reg  <= 64'd0;
            hidden_layer_2_reg  <= 32'd0;

            classification_reg  <= 1'b0;

            stage               <= STAGE_IDLE;
            start_seen          <= 1'b0;
            hidden_layer_2_start <= 1'b0;

            busy                <= 1'b0;
            inference_done      <= 1'b0;

            input_layer_cycles_reg     <= 32'd0;
            hidden_layer_1_cycles_reg  <= 32'd0;
            hidden_layer_2_cycles_reg  <= 32'd0;
            output_layer_cycles_reg    <= 32'd0;

            inference_cycle_count_reg  <= 32'd0;
            total_inference_cycles_reg <= 32'd0;

        end
        else begin

            inference_done       <= 1'b0;
            hidden_layer_2_start <= 1'b0;

            if (!start)
                start_seen <= 1'b0;

            // ----------------------------------------------------
            // START: Capture preprocessed features
            // ----------------------------------------------------

            if (start && !start_seen && !busy) begin

                preprocessed_reg <= features;

                busy       <= 1'b1;
                start_seen <= 1'b1;

                stage <= STAGE_L0;

                input_layer_cycles_reg     <= 32'd0;
                hidden_layer_1_cycles_reg  <= 32'd0;
                hidden_layer_2_cycles_reg  <= 32'd0;
                output_layer_cycles_reg    <= 32'd0;

                inference_cycle_count_reg  <= 32'd0;
                total_inference_cycles_reg <= 32'd0;

            end

            // ----------------------------------------------------
            // STAGE 1: Input layer
            // ----------------------------------------------------

            else if (busy && stage == STAGE_L0) begin

                input_layer_reg <= input_layer_comb;

                input_layer_cycles_reg <=
                    input_layer_cycles_reg + 1'b1;

                inference_cycle_count_reg <=
                    inference_cycle_count_reg + 1'b1;

                stage <= STAGE_L1;

            end

            // ----------------------------------------------------
            // STAGE 2: Hidden layer 1
            // ----------------------------------------------------

            else if (busy && stage == STAGE_L1) begin

                hidden_layer_1_reg <= hidden_layer_1_comb;

                hidden_layer_1_cycles_reg <=
                    hidden_layer_1_cycles_reg + 1'b1;

                inference_cycle_count_reg <=
                    inference_cycle_count_reg + 1'b1;

                // Start hidden layer 2 exactly once.
                hidden_layer_2_start <= 1'b1;

                stage <= STAGE_L2;

            end

            // ----------------------------------------------------
            // STAGE 3: Pipelined hidden layer 2
            // ----------------------------------------------------

            else if (busy && stage == STAGE_L2) begin

                hidden_layer_2_cycles_reg <=
                    hidden_layer_2_cycles_reg + 1'b1;

                inference_cycle_count_reg <=
                    inference_cycle_count_reg + 1'b1;

                // Wait until the registered layer output is ready.
                if (hidden_layer_2_done) begin

                    hidden_layer_2_reg <= hidden_layer_2_comb;

                    stage <= STAGE_OUTPUT;

                end

            end

            // ----------------------------------------------------
            // STAGE 4: Output layer
            // ----------------------------------------------------

            else if (busy && stage == STAGE_OUTPUT) begin

                classification_reg <= output_comb;

                output_layer_cycles_reg <=
                    output_layer_cycles_reg + 1'b1;

                inference_cycle_count_reg <=
                    inference_cycle_count_reg + 1'b1;

                total_inference_cycles_reg <=
                    inference_cycle_count_reg + 1'b1;

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