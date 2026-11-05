
`timescale 1ns / 1ps

module accumulator #(
    parameter INPUT_COUNT = 16,
    parameter INPUT_WIDTH = 8,
    parameter ACC_WIDTH   = 16,
    parameter GROUP_COUNT = 4
)(
    input wire clk,
    input wire rst,
    input wire enable,

    input wire [INPUT_COUNT*INPUT_WIDTH-1:0] inputs,
    input wire [INPUT_COUNT-1:0] weights,

    output reg signed [ACC_WIDTH-1:0] sum,
    output reg done
);

    localparam GROUP_SIZE =
        (INPUT_COUNT + GROUP_COUNT - 1) / GROUP_COUNT;

    // Stage 1: combinational partial sums
    reg signed [ACC_WIDTH-1:0] partial_comb [0:GROUP_COUNT-1];

    // Stage 1: registered partial sums
    reg signed [ACC_WIDTH-1:0] partial_reg [0:GROUP_COUNT-1];

    // Stage 2: final sum
    reg signed [ACC_WIDTH-1:0] sum_comb;

    reg stage1_valid;

    reg [INPUT_WIDTH-1:0] input_value;
    reg signed [ACC_WIDTH-1:0] term;

    integer i;
    integer g_partial;
    integer g_sum;

    // ============================================================
    // STAGE 1: PARTIAL ACCUMULATION
    // ============================================================

    always @(*) begin

        for (g_partial = 0; g_partial < GROUP_COUNT; g_partial = g_partial + 1)
            partial_comb[g_partial] = {ACC_WIDTH{1'b0}};

        input_value = {INPUT_WIDTH{1'b0}};
        term = {ACC_WIDTH{1'b0}};

        for (i = 0; i < INPUT_COUNT; i = i + 1) begin

            input_value = inputs[i*INPUT_WIDTH +: INPUT_WIDTH];

            term = $signed({1'b0, input_value});

            if (weights[i])
                partial_comb[i / GROUP_SIZE] =
                    partial_comb[i / GROUP_SIZE] + term;
            else
                partial_comb[i / GROUP_SIZE] =
                    partial_comb[i / GROUP_SIZE] - term;

        end
    end

    // ============================================================
    // STAGE 2: FINAL ACCUMULATION
    // ============================================================

    always @(*) begin

        sum_comb = {ACC_WIDTH{1'b0}};

        for (g_sum = 0; g_sum < GROUP_COUNT; g_sum = g_sum + 1)
            sum_comb = sum_comb + partial_reg[g_sum];

    end

    // ============================================================
    // PIPELINE REGISTERS
    // ============================================================

    integer k;

    always @(posedge clk) begin

        if (rst) begin

            sum         <= {ACC_WIDTH{1'b0}};
            done        <= 1'b0;
            stage1_valid <= 1'b0;

            for (k = 0; k < GROUP_COUNT; k = k + 1)
                partial_reg[k] <= {ACC_WIDTH{1'b0}};

        end
        else begin

            // Stage 1
            stage1_valid <= enable;

            if (enable) begin
                for (k = 0; k < GROUP_COUNT; k = k + 1)
                    partial_reg[k] <= partial_comb[k];
            end

            // Stage 2
            done <= stage1_valid;

            if (stage1_valid)
                sum <= sum_comb;

        end
    end

endmodule