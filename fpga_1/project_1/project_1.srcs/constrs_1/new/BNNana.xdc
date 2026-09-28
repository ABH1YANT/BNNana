## ============================================================
## BNNana FPGA - Arty A7-100
## FPGA: XC7A100TCSG324-1
## ============================================================


## ============================================================
## 1. SYSTEM CLOCK
## ============================================================
## Arty A7 onboard 100 MHz oscillator

set_property PACKAGE_PIN E3 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]

create_clock -period 10.000 -name sys_clk -waveform {0.000 5.000} [get_ports clk]


## ============================================================
## 2. USB-UART RX
## ============================================================
## Laptop/PC -> USB cable -> onboard USB-UART -> FPGA
##
## D10 = FPGA receives UART data

set_property PACKAGE_PIN D10 [get_ports uart_rx_pin]
set_property IOSTANDARD LVCMOS33 [get_ports uart_rx_pin]


## ============================================================
## 3. USB-UART TX
## ============================================================
## FPGA -> onboard USB-UART -> USB cable -> Laptop/PC
##
## A9 = FPGA transmits UART data

set_property PACKAGE_PIN A9 [get_ports uart_tx_pin]
set_property IOSTANDARD LVCMOS33 [get_ports uart_tx_pin]


## ============================================================
## 4. RESET
## ============================================================
## RESET is currently NOT connected to a physical board pin.
##
## The current fpga_top has:
##
##     input wire rst
##
## We will handle/reset this separately rather than assigning
## an arbitrary FPGA pin.
##
## DO NOT add a PACKAGE_PIN constraint for rst yet.