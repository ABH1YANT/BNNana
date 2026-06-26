`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/26/2026 01:57:46 AM
// Design Name: 
// Module Name: tb_controller_fsm
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


module tb_controller_fsm();

    parameter CLK_PERIOD = 10;

    reg clk;
    reg rst;
    reg packet_valid;
    reg classification;
    reg tx_busy;
    
    wire load_enable;
    wire [7:0] tx_data;
    wire tx_start;

    // Instantiate the Unit Under Test (UUT)
    controller_fsm uut (
        .clk(clk),
        .rst(rst),
        .packet_valid(packet_valid),
        .load_enable(load_enable),
        .classification(classification),
        .tx_data(tx_data),
        .tx_start(tx_start),
        .tx_busy(tx_busy)
    );

    // Generate 100 MHz Clock
    always #(CLK_PERIOD/2) clk = ~clk;

    initial begin
        // Initialize Inputs
        clk = 0;
        rst = 1;
        packet_valid = 0;
        classification = 0;
        tx_busy = 0;

        #100;
        rst = 0;
        #100;

        $display("--- Starting Controller FSM Simulation ---");

        // ---------------------------------------------------------
        // Test 1: Simulate a DDoS Detection (Classification = 1)
        // ---------------------------------------------------------
        $display("Test 1: Simulating Packet Arrival (DDoS)...");
        
        // 1. Packet Parser says a packet is ready
        packet_valid = 1'b1;
        #CLK_PERIOD;
        packet_valid = 1'b0;

        // 2. Wait for the FSM to pulse load_enable
        @(posedge load_enable);
        $display("SUCCESS: load_enable pulsed.");

        // 3. Neural Network calculates (we force the output to 1)
        classification = 1'b1;

        // 4. Wait for the FSM to trigger the UART Transmitter
        @(posedge tx_start);
        if (tx_data == 8'h01)
            $display("SUCCESS: tx_start pulsed with data 0x01.");
        else
            $display("FAIL: tx_data is wrong.");

        // 5. Simulate the UART Transmitter being busy
        #CLK_PERIOD;
        tx_busy = 1'b1;
        #(CLK_PERIOD * 10); // Busy for a while...
        tx_busy = 1'b0;     // Done transmitting!

        #(CLK_PERIOD * 5);

        // ---------------------------------------------------------
        // Test 2: Simulate Benign Traffic (Classification = 0)
        // ---------------------------------------------------------
        $display("Test 2: Simulating Packet Arrival (Benign)...");
        
        packet_valid = 1'b1;
        #CLK_PERIOD;
        packet_valid = 1'b0;

        classification = 1'b0; // Benign

        @(posedge tx_start);
        if (tx_data == 8'h00)
            $display("SUCCESS: tx_start pulsed with data 0x00.");
        else
            $display("FAIL: tx_data is wrong.");

        #CLK_PERIOD;
        tx_busy = 1'b1;
        #(CLK_PERIOD * 10);
        tx_busy = 1'b0;

        #100;
        $display("--- Simulation Complete ---");
        $finish;
    end

endmodule
