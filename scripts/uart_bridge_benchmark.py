from uart_bridge import UARTBridge
import numpy as np

PORT = "COM4" 
bridge = UARTBridge(PORT)

print(f"Testing connection on {PORT}...")

# FIX: Change 10 to 17 to match your Protocol.pack_request
dummy_features = [0.1] * 17 

for i in range(5):
    print(f"\n--- Sample {i} ---")
    # We use a try-except here so we can see if the STM32 actually responds
    try:
        response = bridge.exchange(dummy_features, debug=True)
        if response:
            print(f"Decoded Response: {response}")
        else:
            print("Result: No response (Timeout).")
    except Exception as e:
        print(f"Error during exchange: {e}")

bridge.close()