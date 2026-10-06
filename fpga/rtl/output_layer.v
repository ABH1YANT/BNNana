`timescale 1ns / 1ps

//////////////////////////////////////////////////////////////////////////////////
// BNNana
// Output Layer
//
// Architecture:
//     160 binary inputs -> 1 binary output
//
// RTL packed input:
//     inputs[159:96] = Layer 0
//     inputs[95:32]  = Layer 1
//     inputs[31:0]   = Layer 2
//
// IMPORTANT:
//
// The RTL activation registers use bit 0 for the first logical
// Python activation bit.
//
// Therefore the Python-exported 160-bit weight must be represented
// with each activation group reversed:
//
//     Layer 0 : 64 bits
//     Layer 1 : 64 bits
//     Layer 2 : 32 bits
//
// The resulting Verilog weight is:
//
//     5F5142B50E3E67CFA5960CF68633F2CDFCF2B99C
//
// Operation:
//     Fixed-weight XNOR
//     -> 160-bit match vector
//     -> popcount
//     -> threshold
//     -> 1-bit output
//////////////////////////////////////////////////////////////////////////////////

module output_layer #(
    parameter INPUT_COUNT = 160
)(
    input  wire [INPUT_COUNT-1:0] inputs,
    output wire                   output_bit
);

    // ============================================================
    // OUTPUT WEIGHT
    //
    // Python-exported weight:
    //
    // F3E67C70AD428AFAB34FCC616F3069A5399D4F3F
    //
    // Python groups:
    //
    //   Layer 0 = F3E67C70AD428AFA
    //   Layer 1 = B34FCC616F3069A5
    //   Layer 2 = 399D4F3F
    //
    // Each group is reversed for the RTL bit indexing convention.
    //
    // RTL weight:
    //
    //   Layer 0 = 5F5142B50E3E67CF
    //   Layer 1 = A5960CF68633F2CD
    //   Layer 2 = FCF2B99C
    //
    // Combined:
    //
    //   5F5142B50E3E67CFA5960CF68633F2CDFCF2B99C
    // ============================================================

    wire [159:0] weights;

    assign weights =
        160'h5F5142B50E3E67CFA5960CF68633F2CDFCF2B99C;


    // ============================================================
    // OUTPUT THRESHOLD
    //
    // Python threshold:
    //     0051 = 81
    //
    // Final binary linear layer:
    //
    //     logit = 2 * match_count - 160
    //
    // Python classification:
    //
    //     logit > 0
    //
    // Therefore:
    //
    //     match_count > 80
    //
    // Equivalent integer comparison:
    //
    //     match_count >= 81
    // ============================================================

    wire [7:0] threshold;

    assign threshold = 8'd81;


    // ============================================================
    // FIXED-WEIGHT XNOR
    //
    // weight = 1 -> input matches
    // weight = 0 -> input inverted
    // ============================================================

    wire [159:0] match_bits;

    assign match_bits = ~(inputs ^ weights);


    // ============================================================
    // 160-BIT POPCOUNT
    //
    // Range:
    //     0 .. 160
    //
    // 8 bits are sufficient.
    // ============================================================

    reg [7:0] match_count;

    integer i;

    always @(*) begin

        match_count = 8'd0;

        for (i = 0; i < INPUT_COUNT; i = i + 1) begin

            match_count =
                match_count +
                match_bits[i];

        end

    end


    // ============================================================
    // FINAL CLASSIFICATION
    //
    // count >= 81 -> 1
    // count <  81 -> 0
    //
    // Equivalent to Python:
    //
    //     logit > 0
    // ============================================================

    assign output_bit = (match_count >= threshold);

endmodule