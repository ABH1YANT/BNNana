`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/24/2026 01:57:00 AM
// Design Name: 
// Module Name: tb_packet_parser
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


module tb_packet_parser();

    parameter FEATURE_COUNT = 15;
    parameter START_BYTE = 8'hAA;
    parameter CLK_PERIOD = 10;

    reg clk;
    reg rst;
    reg [7:0] rx_data;
    reg rx_valid;
    
    wire [(FEATURE_COUNT * 8)-1:0] feature_vector;
    wire packet_valid;

    // Instantiate the Unit Under Test (UUT)
    packet_parser #(
        .FEATURE_COUNT(FEATURE_COUNT),
        .START_BYTE(START_BYTE)
    ) uut (
        .clk(clk),
        .rst(rst),
        .rx_data(rx_data),
        .rx_valid(rx_valid),
        .feature_vector(feature_vector),
        .packet_valid(packet_valid)
    );

    // Generate 100 MHz Clock
    always #(CLK_PERIOD/2) clk = ~clk;

    // Task to simulate the UART Controller sending a byte
    task send_uart_byte;
        input [7:0] data;
        begin
            rx_data = data;
            rx_valid = 1'b1;
            #CLK_PERIOD; // Pulse valid for exactly 1 clock cycle
            rx_valid = 1'b0;
            #(CLK_PERIOD * 10); // Wait a bit before the next byte arrives
        end
    endtask

    // --- THE PULSE CATCHER ---
    // This runs in the background and catches the 10ns pulse
    reg pulse_caught;
    always @(posedge packet_valid) begin
        pulse_caught = 1'b1;
    end

    integer i;
    reg [7:0] expected_checksum;

    initial begin
        clk = 0;
        rst = 1;
        rx_data = 0;
        rx_valid = 0;
        pulse_caught = 0;

        #100;
        rst = 0;
        #100;

        $display("--- Starting Packet Parser Simulation ---");

        // ---------------------------------------------------------
        // Test 1: Perfect Packet
        // ---------------------------------------------------------
        $display("Test 1: Sending Perfect Packet...");
        expected_checksum = 0;
        pulse_caught = 0; // Reset the catcher flag
        
        send_uart_byte(START_BYTE); // Send 0xAA
        
        for (i = 1; i <= FEATURE_COUNT; i = i + 1) begin
            send_uart_byte(i); // Send features 1, 2, 3... 15
            expected_checksum = expected_checksum + i;
        end
        
        // Send the correct checksum
        send_uart_byte(expected_checksum); 
        
        #50;
        // Check our flag instead of the raw wire
        if (pulse_caught == 1'b1)
            $display("SUCCESS: packet_valid pulsed! Checksum matched (0x%h).", expected_checksum);
        else
            $display("FAIL: packet_valid did not pulse.");

        #100;

        // ---------------------------------------------------------
        // Test 2: Wrong Start Byte (Noise on the line)
        // ---------------------------------------------------------
        $display("Test 2: Sending Packet with Wrong Start Byte (0xBB)...");
        pulse_caught = 0; // Reset flag
        
        send_uart_byte(8'hBB); // Wrong start byte
        for (i = 1; i <= FEATURE_COUNT; i = i + 1) send_uart_byte(i);
        send_uart_byte(expected_checksum);
        
        #50;
        if (pulse_caught == 1'b0)
            $display("SUCCESS: Ignored bad start byte.");
        else
            $display("FAIL: It accepted a bad start byte!");

        #100;

        // ---------------------------------------------------------
        // Test 3: Corrupted Checksum
        // ---------------------------------------------------------
        $display("Test 3: Sending Packet with Corrupted Checksum...");
        pulse_caught = 0; // Reset flag
        
        send_uart_byte(START_BYTE);
        for (i = 1; i <= FEATURE_COUNT; i = i + 1) send_uart_byte(i);
        
        // Send a bad checksum (0xFF instead of 0x78)
        send_uart_byte(8'hFF); 
        
        #50;
        if (pulse_caught == 1'b0)
            $display("SUCCESS: Ignored bad checksum.");
        else
            $display("FAIL: It accepted a bad checksum!");

        #100;
        $display("--- Simulation Complete ---");
        $finish;
    end

endmodule
