
`timescale 1ns / 1ps

module threshold_compare #(
    parameter COUNT_WIDTH = 7
)(
    input wire clk,
    input wire rst,
    input wire enable,

    input wire [COUNT_WIDTH-1:0] count,
    input wire [COUNT_WIDTH-1:0] threshold,

    output reg output_bit,
    output reg done
);

    // ============================================================
    // REGISTERED THRESHOLD COMPARISON
    // ============================================================

    always @(posedge clk) begin

        if (rst) begin
            output_bit <= 1'b0;
            done       <= 1'b0;
        end

        else begin

            done <= enable;

            if (enable)
                output_bit <= (count >= threshold);

        end

    end

endmodule
