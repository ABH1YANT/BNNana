import struct

class Protocol:
    # Request: Header(1B) + 17 Floats(68B) + Checksum(1B) = 70 Bytes
    # < = Little Endian
    # B = unsigned char (1)
    # 17f = 17 floats (68)
    # B = unsigned char (1)
    REQ_FMT = "<B17fB" 
    REQ_HEADER = 0xAA
    
    # Response: Header(1B) + Pred(1B) + Cycles(4B) + Time_us(2B) + Checksum(1B) = 9 Bytes
    # < = Little Endian
    # B = unsigned char (1) - Header
    # B = unsigned char (1) - Prediction
    # I = unsigned int  (4) - Cycles (uint32_t)
    # H = unsigned short (2) - Latency (uint16_t)  <-- FIXED FROM L TO H
    # B = unsigned char (1) - Checksum
    RES_FMT = "<BBIHB" 
    RES_HEADER = 0x55

    @staticmethod
    def calculate_checksum(data):
        # Matches C: uint8_t sum = 0; sum += data[i];
        return sum(data) & 0xFF

    @classmethod
    def pack_request(cls, features):
        # Pack the 17 floats into binary
        payload = struct.pack("<17f", *features)
        # Calculate checksum of the 68-byte payload
        checksum = cls.calculate_checksum(payload)
        # Wrap with header and checksum
        return struct.pack("<B", cls.REQ_HEADER) + payload + struct.pack("<B", checksum)

    @classmethod
    def unpack_response(cls, raw_data):
        expected_size = struct.calcsize(cls.RES_FMT)
        
        if len(raw_data) != expected_size:
            print(f"Protocol Error: Expected {expected_size} bytes, got {len(raw_data)}")
            return None
        
        header, pred, cycles, time_us, checksum = struct.unpack(cls.RES_FMT, raw_data)
        
        if header != cls.RES_HEADER:
            print(f"Protocol Error: Invalid Header {hex(header)}")
            return None
            
        # Verify checksum of the payload portion (pred + cycles + time_us)
        # raw_data[1:-1] is bytes 1 through 7 (total 7 bytes)
        data_portion = raw_data[1:8] 
        computed_checksum = cls.calculate_checksum(data_portion)
        
        if computed_checksum != checksum:
            print(f"Protocol Error: Checksum Mismatch (Got {hex(checksum)}, Calc {hex(computed_checksum)})")
            return None
            
        return {
            "prediction": pred,
            "cycles": cycles,
            "latency_us": time_us
        }