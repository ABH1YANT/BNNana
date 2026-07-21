import serial
import time
from packet import Protocol

class UARTBridge:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        # Give the MCU a moment to reset after opening the port
        time.sleep(1)
        
    def ping(self):
        """Simple check to see if MCU is alive."""
        self.ser.write(b'\x00')
        return self.ser.read(1) == b'\x01'

    def exchange(self, features, debug=False):
        # Clear buffers to ensure we aren't reading old data
        self.ser.reset_input_buffer()
        
        # Send
        packet = Protocol.pack_request(features)
        self.ser.write(packet)
        
        # Read Response (9 bytes expected)
        response_raw = self.ser.read(9)
        
        if debug:
            print(f"Sent: {packet.hex()}")
            print(f"Received {len(response_raw)} bytes: {response_raw.hex()}")

        if len(response_raw) == 0:
            return None
            
        return Protocol.unpack_response(response_raw)

    def close(self):
        self.ser.close()