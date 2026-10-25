import csv
import os
import time
import math
import statistics
from datetime import datetime

import serial

# ============================================================
# CONFIGURATION
# ============================================================

CSV_PATH = (
    r"C:\Users\DELL\Desktop\BNNana"
    r"\datasets\processed\master_dataset.csv"
)

REPORT_DIR = r"C:\Users\DELL\Desktop\BNNana\reports"

PORT = "COM4"
BAUD = 115200
EXPECTED_ROWS = 10000
RESPONSE_TIMEOUT = 5

# Output filenames
DETAIL_CSV = os.path.join(REPORT_DIR, "mcu_test_results.csv")
SUMMARY_TXT = os.path.join(REPORT_DIR, "mcu_test_results_summary.txt")

FEATURES = [
    "Bwd Packet Length Max",
    "Min Packet Length",
    "Subflow Bwd Bytes",
    "Total Length of Bwd Packets",
    "Destination Port",
    "min_seg_size_forward",
    "ACK Flag Count",
    "Subflow Bwd Packets",
    "Fwd Packet Length Max",
    "Total Backward Packets",
    "Subflow Fwd Bytes",
    "Max Packet Length",
    "Total Length of Fwd Packets",
    "Bwd Header Length",
    "Flow Duration",
    "Fwd Header Length",
]


# ============================================================
# SERIAL RESPONSE
# ============================================================

def read_response(ser):
    """Wait for a prediction or firmware error, with a timeout."""
    deadline = time.monotonic() + RESPONSE_TIMEOUT

    while time.monotonic() < deadline:
        line = ser.readline().decode(
            "utf-8", errors="replace"
        ).strip()

        if line.startswith("PRED,") or line.startswith("ERR,"):
            return line

    return None


# ============================================================
# LOAD DATASET
# ============================================================

os.makedirs(REPORT_DIR, exist_ok=True)

with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    required = FEATURES + ["Label"]
    missing = [
        name for name in required
        if name not in (reader.fieldnames or [])
    ]

    if missing:
        raise ValueError(f"Missing CSV columns: {missing}")

    rows = []

    for row in reader:
        features = [int(row[name]) for name in FEATURES]
        label = int(row["Label"])

        if label not in (0, 1):
            raise ValueError(f"Unexpected label: {label}")

        if any(value < 0 for value in features):
            raise ValueError("Negative raw feature encountered")

        rows.append((features, label))

        if len(rows) >= EXPECTED_ROWS:
            break

if not rows:
    raise ValueError("The dataset contains no rows.")

if len(rows) < EXPECTED_ROWS:
    raise ValueError(
        f"Requested {EXPECTED_ROWS} rows, but only "
        f"{len(rows)} are available."
    )

print("=" * 60)
print("BNNana ESP32 MCU TEST")
print("=" * 60)
print(f"Dataset: {CSV_PATH}")
print(f"Rows: {len(rows)}")
print(f"Features per row: {len(FEATURES)}")
print(f"Serial port: {PORT}")
print(f"Baud rate: {BAUD}")
print(f"Reports directory: {REPORT_DIR}")
print("\nConnecting to ESP32...")


# ============================================================
# RUN ESP32 INFERENCE AND MEASURE EACH TRANSACTION
# ============================================================

# Each result contains every feature, label, prediction,
# correctness, transaction timing, and status.
results = []
run_errors = []

run_start = time.perf_counter()
test_started_at = datetime.now().astimezone().isoformat()

try:
    with serial.Serial(
        PORT,
        BAUD,
        timeout=0.2,
        write_timeout=RESPONSE_TIMEOUT,
    ) as ser:

        # Opening the port may reset the ESP32.
        time.sleep(2)
        ser.reset_input_buffer()

        print("Serial connection ready.\n")

        for index, (features, label) in enumerate(rows, start=1):
            payload = ",".join(str(value) for value in features)
            payload_bytes = (payload + "\n").encode("ascii")

            prediction = None
            response = ""
            status = ""
            error_message = ""
            tx_start = time.perf_counter()

            try:
                # Start timing immediately before sending the packet.
                ser.write(payload_bytes)
                ser.flush()

                # Wait for ESP32 preprocessing, inference, and reply.
                response = read_response(ser)

                if response is None:
                    status = "TIMEOUT"
                    error_message = (
                        f"No PRED/ERR response within "
                        f"{RESPONSE_TIMEOUT} seconds"
                    )

                elif response.startswith("ERR,"):
                    status = "FIRMWARE_ERROR"
                    error_message = response

                else:
                    try:
                        prediction = int(response.split(",", 1)[1])

                        if prediction not in (0, 1):
                            status = "INVALID_PREDICTION"
                            error_message = str(prediction)
                            prediction = None
                        else:
                            status = (
                                "OK" if prediction == label
                                else "MISMATCH"
                            )

                    except (ValueError, IndexError):
                        status = "INVALID_RESPONSE"
                        error_message = response

            except (serial.SerialException, serial.SerialTimeoutException) as exc:
                status = "SERIAL_ERROR"
                error_message = str(exc)

            # Includes serial transmission, ESP32 work, and reply.
            latency_ms = (time.perf_counter() - tx_start) * 1000.0

            correct = (
                prediction == label
                if prediction is not None
                else None
            )

            result = {
                "row": index,
                "features": features,
                "label": label,
                "prediction": prediction,
                "correct": correct,
                "latency_ms": latency_ms,
                "response": response,
                "status": status,
                "error": error_message,
            }

            results.append(result)

            if status not in ("OK", "MISMATCH"):
                run_errors.append((index, status, error_message))

            # Print periodic progress to avoid flooding the terminal.
            if index == 1 or index % 100 == 0 or index == len(rows):
                valid_count = sum(
                    r["prediction"] is not None for r in results
                )
                correct_count = sum(
                    r["correct"] is True for r in results
                )
                current_accuracy = (
                    100.0 * correct_count / valid_count
                    if valid_count else 0.0
                )

                print(
                    f"[{index:5}/{len(rows)}] "
                    f"latency={latency_ms:9.3f} ms | "
                    f"status={status:18} | "
                    f"running accuracy={current_accuracy:6.2f}%"
                )

except serial.SerialException as exc:
    print(f"\nCould not use serial port {PORT}: {exc}")
    print("Close any serial monitor and check the USB connection.")
    raise

run_end = time.perf_counter()
total_elapsed_s = run_end - run_start
test_finished_at = datetime.now().astimezone().isoformat()


# ============================================================
# CALCULATE METRICS
# ============================================================

total_rows = len(rows)

valid_results = [
    r for r in results
    if r["prediction"] in (0, 1)
]

correct_results = [
    r for r in valid_results
    if r["correct"] is True
]

incorrect_results = [
    r for r in valid_results
    if r["correct"] is False
]

valid_count = len(valid_results)
correct_count = len(correct_results)
incorrect_count = len(incorrect_results)
failed_count = total_rows - valid_count

accuracy = (
    100.0 * correct_count / valid_count
    if valid_count else 0.0
)

latencies = [r["latency_ms"] for r in results]

valid_latencies = [
    r["latency_ms"] for r in valid_results
]


def percentile(values, percent):
    """Linearly interpolated percentile."""
    if not values:
        return None

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = (len(ordered) - 1) * percent / 100.0
    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return ordered[lower]

    fraction = position - lower

    return (
        ordered[lower] * (1.0 - fraction)
        + ordered[upper] * fraction
    )


def format_ms(value):
    return f"{value:.3f} ms" if value is not None else "N/A"


# Confusion matrix from valid predictions only.
tn = sum(
    r["label"] == 0 and r["prediction"] == 0
    for r in valid_results
)
fp = sum(
    r["label"] == 0 and r["prediction"] == 1
    for r in valid_results
)
fn = sum(
    r["label"] == 1 and r["prediction"] == 0
    for r in valid_results
)
tp = sum(
    r["label"] == 1 and r["prediction"] == 1
    for r in valid_results
)

precision = tp / (tp + fp) if tp + fp else 0.0
recall = tp / (tp + fn) if tp + fn else 0.0
specificity = tn / (tn + fp) if tn + fp else 0.0
f1 = (
    2 * precision * recall / (precision + recall)
    if precision + recall else 0.0
)

throughput = (
    total_rows / total_elapsed_s
    if total_elapsed_s > 0 else 0.0
)

mean_latency = (
    statistics.mean(latencies) if latencies else None
)
median_latency = percentile(latencies, 50)
p95_latency = percentile(latencies, 95)
p99_latency = percentile(latencies, 99)
min_latency = min(latencies) if latencies else None
max_latency = max(latencies) if latencies else None

mean_valid_latency = (
    statistics.mean(valid_latencies)
    if valid_latencies else None
)


# ============================================================
# SAVE PER-ROW DETAIL CSV
# ============================================================

detail_columns = [
    "Row",
    *FEATURES,
    "Label",
    "Prediction",
    "Correct",
    "Latency_ms",
    "Status",
    "ESP32_Response",
    "Error",
]

with open(DETAIL_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=detail_columns)
    writer.writeheader()

    for result in results:
        output_row = {
            "Row": result["row"],
            "Label": result["label"],
            "Prediction": (
                result["prediction"]
                if result["prediction"] is not None else ""
            ),
            "Correct": (
                result["correct"]
                if result["correct"] is not None else ""
            ),
            "Latency_ms": f'{result["latency_ms"]:.3f}',
            "Status": result["status"],
            "ESP32_Response": result["response"],
            "Error": result["error"],
        }

        for feature_name, value in zip(FEATURES, result["features"]):
            output_row[feature_name] = value

        writer.writerow(output_row)


# ============================================================
# SAVE DETAILED SUMMARY REPORT
# ============================================================

summary_lines = [
    "BNNana ESP32 MCU TEST RESULTS",
    "=" * 60,
    "",
    "TEST CONFIGURATION",
    "-" * 60,
    f"Started: {test_started_at}",
    f"Finished: {test_finished_at}",
    f"Dataset: {CSV_PATH}",
    f"Serial port: {PORT}",
    f"Baud rate: {BAUD}",
    f"Features per packet: {len(FEATURES)}",
    f"Rows requested: {EXPECTED_ROWS}",
    f"Rows processed: {len(results)}",
    f"Response timeout: {RESPONSE_TIMEOUT} seconds",
    "",
    "CLASSIFICATION RESULTS",
    "-" * 60,
    f"Valid predictions: {valid_count}",
    f"Correct predictions: {correct_count}",
    f"Incorrect predictions: {incorrect_count}",
    f"Rows without valid predictions: {failed_count}",
    f"Accuracy among valid predictions: {accuracy:.4f}%",
    f"Accuracy over all requested rows: "
    f"{100.0 * correct_count / total_rows:.4f}%",
    f"Precision (class 1): {precision * 100:.4f}%",
    f"Recall (class 1): {recall * 100:.4f}%",
    f"Specificity (class 0): {specificity * 100:.4f}%",
    f"F1 score (class 1): {f1 * 100:.4f}%",
    "",
    "CONFUSION MATRIX (VALID PREDICTIONS ONLY)",
    "-" * 60,
    "                 Predicted 0    Predicted 1",
    f"Actual 0 (TN/FP) {tn:12}    {fp:12}",
    f"Actual 1 (FN/TP) {fn:12}    {tp:12}",
    "",
    "TIMING RESULTS",
    "-" * 60,
    "Timing measures PC-to-ESP32 serial round-trip latency.",
    "It includes packet transmission, ESP32 preprocessing/inference,",
    "and the response transmission. It is not inference-only timing.",
    f"Total elapsed time: {total_elapsed_s:.3f} seconds",
    f"Mean latency per row: {format_ms(mean_latency)}",
    f"Mean latency for valid predictions: {format_ms(mean_valid_latency)}",
    f"Median latency (P50): {format_ms(median_latency)}",
    f"95th percentile latency (P95): {format_ms(p95_latency)}",
    f"99th percentile latency (P99): {format_ms(p99_latency)}",
    f"Minimum latency: {format_ms(min_latency)}",
    f"Maximum latency: {format_ms(max_latency)}",
    f"Throughput: {throughput:.3f} rows/second",
    "",
    "SERIAL / FIRMWARE ERRORS",
    "-" * 60,
    f"Total errors or invalid responses: {len(run_errors)}",
]

if run_errors:
    summary_lines.append("")
    for row_number, status, message in run_errors:
        summary_lines.append(
            f"Row {row_number}: {status} - {message}"
        )
else:
    summary_lines.append("No serial errors, timeouts, or invalid responses.")

summary_lines.extend([
    "",
    "FEATURE ORDER USED",
    "-" * 60,
])

for i, name in enumerate(FEATURES, start=1):
    summary_lines.append(f"{i:02}. {name}")

summary_lines.extend([
    "",
    "OUTPUT FILES",
    "-" * 60,
    f"Per-row detailed results: {DETAIL_CSV}",
    f"Summary report: {SUMMARY_TXT}",
    "",
    "INTERPRETATION NOTES",
    "-" * 60,
    "Accuracy is calculated against the CSV Label column.",
    "A high dataset accuracy alone does not prove that the ESP32",
    "matches the original PyTorch model. Compare predictions from",
    "both implementations on identical inputs to validate parity.",
    "The dataset rows may not be independent of training data.",
    "Check the dataset split before claiming generalization.",
])

with open(SUMMARY_TXT, "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines) + "\n")


# ============================================================
# PRINT FINAL REPORT
# ============================================================

print("\n" + "=" * 60)
print("ESP32 MCU TEST RESULTS")
print("=" * 60)
print(f"Dataset rows:              {total_rows}")
print(f"Valid predictions:         {valid_count}")
print(f"Correct predictions:       {correct_count}")
print(f"Incorrect predictions:     {incorrect_count}")
print(f"Errors/invalid responses:  {failed_count}")
print(f"Accuracy:                  {accuracy:.2f}%")

print("\nConfusion matrix (valid predictions only)")
print("                 Predicted 0  Predicted 1")
print(f"Actual 0 (TN/FP) {tn:12}  {fp:12}")
print(f"Actual 1 (FN/TP) {fn:12}  {tp:12}")

print("\nTiming")
print(f"Total elapsed:       {total_elapsed_s:.3f} s")
print(f"Average per packet:  {format_ms(mean_latency)}")
print(f"Median (P50):        {format_ms(median_latency)}")
print(f"P95:                 {format_ms(p95_latency)}")
print(f"P99:                 {format_ms(p99_latency)}")
print(f"Minimum:             {format_ms(min_latency)}")
print(f"Maximum:             {format_ms(max_latency)}")
print(f"Throughput:          {throughput:.2f} packets/s")

print("\nSaved reports:")
print(DETAIL_CSV)
print(SUMMARY_TXT)
print("=" * 60)
