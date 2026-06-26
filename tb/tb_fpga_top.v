`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 06/26/2026 02:09:41 AM
// Design Name: 
// Module Name: tb_fpga_top
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


module tb_fpga_top();

    parameter CLKS_PER_BIT = 868;
    parameter CLK_PERIOD = 10;
    parameter FEATURE_COUNT = 15;

    reg clk;
    reg rst;
    reg rx;
    wire tx;

    // Instantiate the Top Module
    fpga_top #(
        .CLKS_PER_BIT(CLKS_PER_BIT),
        .FEATURE_COUNT(FEATURE_COUNT)
    ) uut (
        .clk(clk),
        .rst(rst),
        .rx(rx),
        .tx(tx)
    );

    // Generate 100 MHz Clock
    always #(CLK_PERIOD/2) clk = ~clk;

    // PC Simulator: Send Byte Task
    task send_byte;
        input [7:0] data;
        integer i;
        begin
            rx = 1'b0; #(CLK_PERIOD * CLKS_PER_BIT); // Start bit
            for (i = 0; i < 8; i = i + 1) begin
                rx = data[i]; #(CLK_PERIOD * CLKS_PER_BIT); // Data bits
            end
            rx = 1'b1; #(CLK_PERIOD * CLKS_PER_BIT); // Stop bit
            
            // REALISM FIX: Tiny gap between bytes to let the FPGA reset its state machine
            #(CLK_PERIOD * 10); 
        end
    endtask

    // PC Simulator: Receive Byte Task
    reg [7:0] received_byte;
    task receive_byte;
        integer k;
        begin
            @(negedge tx); 
            #(CLK_PERIOD * (CLKS_PER_BIT / 2)); 
            #(CLK_PERIOD * CLKS_PER_BIT); 
            for (k = 0; k < 8; k = k + 1) begin
                received_byte[k] = tx;
                #(CLK_PERIOD * CLKS_PER_BIT);
            end
            #(CLK_PERIOD * CLKS_PER_BIT); 
        end
    endtask

    // --- INTERNAL HARDWARE PROBES ---
    // These print exactly what is happening inside the FPGA
    always @(posedge uut.parser_inst.rx_valid) begin
        if (uut.parser_inst.state == 2'b10) begin // WAIT_CHECKSUM state
            $display("   [PROBE] Parser checking Checksum. Received: %d | Calculated: %d", uut.parser_inst.rx_data, uut.parser_inst.calculated_checksum);
        end
    end
    always @(posedge uut.parser_inst.packet_valid) $display("   [PROBE] packet_valid pulsed! Packet is perfect.");
    always @(posedge uut.fsm_inst.load_enable) $display("   [PROBE] FSM load_enable pulsed! Features locked.");
    always @(posedge uut.fsm_inst.tx_start) $display("   [PROBE] FSM tx_start pulsed! Sending classification: 0x%h", uut.fsm_inst.tx_data);

    integer j;
    reg [7:0] checksum;

    initial begin
        clk = 0;
        rst = 1;
        rx = 1;

        #100;
        rst = 0;
        #100;

        $display("--- Starting FULL SYSTEM End-to-End Test ---");
        $display("PC: Sending Network Packet to FPGA...");

        // 1. Send Start Byte
        send_byte(8'hAA);
        checksum = 0;

        // 2. Send 15 Features (We will send '1' for all features)
        for (j = 0; j < FEATURE_COUNT; j = j + 1) begin
            send_byte(8'd1);
            checksum = checksum + 8'd1;
        end

        // 3. Send Checksum AND Listen for Response at the same time!
        fork
            begin
                send_byte(checksum);
                $display("PC: Packet sent successfully.");
            end
            begin
                receive_byte(); // PC listens while finishing the send
                $display("PC: Received Classification from FPGA: 0x%h", received_byte);
                
                if (received_byte == 8'h01)
                    $display("RESULT: DDoS Attack Detected!");
                else if (received_byte == 8'h00)
                    $display("RESULT: Traffic is Benign. (SUCCESS!)");
                else
                    $display("RESULT: ERROR - Unknown response.");
            end
        join

        #1000;
        $display("--- System Simulation Complete ---");
        $finish;
    end

endmodule