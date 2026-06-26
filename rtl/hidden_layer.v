`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/23/2026 12:57:28 AM
// Design Name: 
// Module Name: hidden_layer
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module hidden_layer #(
    parameter INPUT_COUNT = 15,
    parameter NEURON_COUNT = 16,
    parameter INPUT_WIDTH = 8,
    parameter ACC_WIDTH = 16
)(
    input wire [(INPUT_COUNT * INPUT_WIDTH)-1:0] feature_vector,
    input wire [(NEURON_COUNT * INPUT_COUNT)-1:0] all_hidden_weights,
    input wire [(NEURON_COUNT * ACC_WIDTH)-1:0] all_hidden_thresholds,
    output wire [NEURON_COUNT-1:0] hidden_outputs
);

    genvar i;
    generate
        for (i = 0; i < NEURON_COUNT; i = i + 1) begin : hidden_neurons
            bwn_neuron #(
                .INPUT_COUNT(INPUT_COUNT),
                .INPUT_WIDTH(INPUT_WIDTH),
                .ACC_WIDTH(ACC_WIDTH)
            ) neuron_inst (
                // Broadcast the exact same features to all 16 neurons
                .feature_vector(feature_vector),
                
                // Slice the massive weight bus: 15 bits per neuron
                .weight_vector(all_hidden_weights[i * INPUT_COUNT +: INPUT_COUNT]),
                
                // Slice the massive threshold bus: 16 bits per neuron
                .threshold(all_hidden_thresholds[i * ACC_WIDTH +: ACC_WIDTH]),
                
                // Connect to the specific bit of the output bus
                .neuron_out(hidden_outputs[i])
            );
        end
    endgenerate

endmodule
