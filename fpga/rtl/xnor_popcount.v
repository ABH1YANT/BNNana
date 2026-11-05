
`timescale 1ns / 1ps

module xnor_popcount #(
    parameter WIDTH = 64,
    parameter GROUP_SIZE = 8,
    parameter GROUP_COUNT = (WIDTH + GROUP_SIZE - 1) / GROUP_SIZE
)(
    input wire clk,
    input wire rst,
    input wire enable,

    input wire [WIDTH-1:0] inputs,
    input wire [WIDTH-1:0] weights,

    output reg [WIDTH-1:0] matches,
    output reg [6:0] count,
    output reg done
);

    // ============================================================
    // INTERMEDIATE SIGNALS
    // ============================================================

    wire [WIDTH-1:0] xnor_comb;

    reg [3:0] partial_comb [0:GROUP_COUNT-1];
    reg [3:0] partial_reg  [0:GROUP_COUNT-1];

    reg [6:0] count_comb;

    // Pipeline valid signals
    reg stage1_valid;
    reg stage2_valid;

    integer g_comb;
    integer b_comb;
    integer g_sum;
    integer reset_idx;

    // ============================================================
    // STAGE 1: XNOR
    // ============================================================

    assign xnor_comb = ~(inputs ^ weights);

    // ============================================================
    // STAGE 2: PARTIAL POPCOUNT
    // Eight groups of eight bits for WIDTH=64
    // ============================================================

    always @(*) begin

        for (g_comb = 0; g_comb < GROUP_COUNT; g_comb = g_comb + 1)
            partial_comb[g_comb] = 4'd0;

        for (g_comb = 0; g_comb < GROUP_COUNT; g_comb = g_comb + 1) begin

            for (b_comb = 0; b_comb < GROUP_SIZE; b_comb = b_comb + 1) begin

                if ((g_comb * GROUP_SIZE + b_comb) < WIDTH) begin

                    partial_comb[g_comb] =
                        partial_comb[g_comb] +
                        matches[g_comb * GROUP_SIZE + b_comb];

                end

            end

        end

    end

    // ============================================================
    // STAGE 3: FINAL POPCOUNT
    // ============================================================

    always @(*) begin

        count_comb = 7'd0;

        for (g_sum = 0; g_sum < GROUP_COUNT; g_sum = g_sum + 1)
            count_comb = count_comb + partial_reg[g_sum];

    end

    // ============================================================
    // PIPELINE REGISTERS
    // ============================================================

    always @(posedge clk) begin

        if (rst) begin

            matches <= {WIDTH{1'b0}};
            count   <= 7'd0;
            done    <= 1'b0;

            stage1_valid <= 1'b0;
            stage2_valid <= 1'b0;

            for (reset_idx = 0; reset_idx < GROUP_COUNT;
                 reset_idx = reset_idx + 1)
                partial_reg[reset_idx] <= 4'd0;

        end

        else begin

            // Stage 1: Register XNOR results
            stage1_valid <= enable;

            if (enable)
                matches <= xnor_comb;

            // Stage 2: Register partial popcounts
            stage2_valid <= stage1_valid;

            if (stage1_valid) begin

                for (reset_idx = 0; reset_idx < GROUP_COUNT;
                     reset_idx = reset_idx + 1)
                    partial_reg[reset_idx] <= partial_comb[reset_idx];

            end

            // Stage 3: Register final count
            done <= stage2_valid;

            if (stage2_valid)
                count <= count_comb;

        end

    end

endmodule
