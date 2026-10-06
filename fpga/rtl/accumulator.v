`timescale 1ns / 1ps

module accumulator #(
    parameter INPUT_COUNT = 16,
    parameter INPUT_WIDTH = 8,
    parameter ACC_WIDTH   = 16
)(
    input wire [INPUT_COUNT*INPUT_WIDTH-1:0] inputs,
    input wire [INPUT_COUNT-1:0] weights,
    output reg signed [ACC_WIDTH-1:0] sum
);

    integer i;
    reg [INPUT_WIDTH-1:0] input_value;

    always @(*) begin
        sum = {ACC_WIDTH{1'b0}};

        for (i = 0; i < INPUT_COUNT; i = i + 1) begin
            input_value = inputs[i*INPUT_WIDTH +: INPUT_WIDTH];

            if (weights[i] == 1'b1)
                sum = sum + input_value;
            else
                sum = sum - input_value;
        end
    end

endmodule