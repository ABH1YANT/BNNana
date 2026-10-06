import serial
import time
import argparse


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_PORT = "COM11"
DEFAULT_BAUD = 115200
DEFAULT_TIMEOUT = 1.0


# ============================================================
# TEST DATA
# ============================================================

TEST_BYTES = [
    0x00,
    0x01,
    0x02,
    0x55,
    0xAA,
    0xFF,
    0x7F,
    0x80,
]


# ============================================================
# TEST ONE BYTE
# ============================================================

def test_byte(ser, value, timeout):

    ser.reset_input_buffer()

    start_time = time.perf_counter()

    ser.write(bytes([value]))
    ser.flush()

    while True:

        data = ser.read(1)

        if data:

            elapsed = (
                time.perf_counter()
                - start_time
            )

            received = data[0]

            if received == value:

                return True, received, elapsed

            return False, received, elapsed

        if (
            time.perf_counter()
            - start_time
            >= timeout
        ):

            return False, None, (
                time.perf_counter()
                - start_time
            )


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="UART-only FPGA loopback test"
    )

    parser.add_argument(
        "--port",
        default=DEFAULT_PORT,
        help=f"Serial port (default: {DEFAULT_PORT})"
    )

    parser.add_argument(
        "--baud",
        type=int,
        default=DEFAULT_BAUD,
        help=f"Baud rate (default: {DEFAULT_BAUD})"
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout in seconds (default: {DEFAULT_TIMEOUT})"
    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # OPEN UART
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("BNNana UART TRANSMISSION TEST")
    print("=" * 60)

    print()
    print(f"Port      : {args.port}")
    print(f"Baud rate : {args.baud}")
    print("Format    : 8-N-1")

    try:

        ser = serial.Serial(
            port=args.port,
            baudrate=args.baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.05
        )

    except Exception as error:

        print()
        print("ERROR: Could not open UART.")
        print(error)
        return

    print()
    print("UART connected.")

    time.sleep(0.2)

    # --------------------------------------------------------
    # BASIC BYTE TEST
    # --------------------------------------------------------

    total = 0
    passed = 0
    failed = 0

    print()
    print("-" * 60)
    print("BASIC BYTE TEST")
    print("-" * 60)

    for value in TEST_BYTES:

        total += 1

        success, received, elapsed = test_byte(
            ser,
            value,
            args.timeout
        )

        if success:

            passed += 1

            print(
                f"TX=0x{value:02X}  "
                f"RX=0x{received:02X}  "
                f"PASS  "
                f"{elapsed * 1000:.3f} ms"
            )

        else:

            failed += 1

            if received is None:

                print(
                    f"TX=0x{value:02X}  "
                    f"RX=TIMEOUT  "
                    f"FAIL"
                )

            else:

                print(
                    f"TX=0x{value:02X}  "
                    f"RX=0x{received:02X}  "
                    f"FAIL"
                )

    # --------------------------------------------------------
    # ALL 256 BYTE VALUES
    # --------------------------------------------------------

    print()
    print("-" * 60)
    print("256-BYTE VALUE TEST")
    print("-" * 60)

    for value in range(256):

        total += 1

        success, received, elapsed = test_byte(
            ser,
            value,
            args.timeout
        )

        if success:

            passed += 1

        else:

            failed += 1

            if received is None:

                print(
                    f"FAIL TX=0x{value:02X} "
                    f"RX=TIMEOUT"
                )

            else:

                print(
                    f"FAIL TX=0x{value:02X} "
                    f"RX=0x{received:02X}"
                )

    # --------------------------------------------------------
    # PATTERN TEST
    # --------------------------------------------------------

    patterns = [
        bytes([0x00] * 32),
        bytes([0xFF] * 32),
        bytes([0x55] * 32),
        bytes([0xAA] * 32),
        bytes(range(32)),
    ]

    print()
    print("-" * 60)
    print("PATTERN TEST")
    print("-" * 60)

    for pattern_index, pattern in enumerate(patterns):

        ser.reset_input_buffer()

        start_time = time.perf_counter()

        ser.write(pattern)
        ser.flush()

        received = bytearray()

        while len(received) < len(pattern):

            data = ser.read(
                len(pattern) - len(received)
            )

            if data:

                received.extend(data)

            if (
                time.perf_counter()
                - start_time
                >= args.timeout
            ):

                break

        elapsed = (
            time.perf_counter()
            - start_time
        )

        if bytes(received) == pattern:

            passed += 1
            total += 1

            print(
                f"Pattern {pattern_index + 1}: "
                f"PASS "
                f"({len(pattern)} bytes, "
                f"{elapsed * 1000:.3f} ms)"
            )

        else:

            failed += 1
            total += 1

            print(
                f"Pattern {pattern_index + 1}: FAIL "
                f"(sent {len(pattern)} bytes, "
                f"received {len(received)} bytes)"
            )

    # --------------------------------------------------------
    # CLOSE UART
    # --------------------------------------------------------

    ser.close()

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("UART TEST COMPLETE")
    print("=" * 60)

    print()
    print(f"Total tests : {total}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")

    if total > 0:

        print(
            f"Pass rate   : "
            f"{passed / total * 100:.2f}%"
        )

    print()

    if failed == 0:

        print("UART TRANSMISSION TEST: PASS")

    else:

        print("UART TRANSMISSION TEST: FAIL")

    print()


if __name__ == "__main__":
    main()