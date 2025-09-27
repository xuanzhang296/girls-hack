import numpy as np
import time
import json  # for JSON serialization
import argparse  # CLI arguments
from datetime import datetime, timezone  # ISO timestamp generation

# Generate example signal (sine + noise)
fs = 1000  # sample rate Hz (one-off demo mode only)
T = 2      # total duration s (one-off demo mode only)
t = np.linspace(0, T, fs*T, endpoint=False)  # time vector (0..T, excluding T)
signalTotal = np.sin(2*np.pi*5*t) + 0.2*np.random.randn(len(t))  # 5Hz sine + noise

# Window parameters
window_size = 200   # samples per window
step_size = 20      # hop length in samples

def iso_utc_now_ms():
    """Return current UTC time in ISO8601 string with millisecond precision (Z)."""
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def main():
    parser = argparse.ArgumentParser(description="Generate sliding-window JSON lines from a signal")
    parser.add_argument("--stream", action="store_true", help="Enable continuous streaming (infinite)")
    parser.add_argument("--interval", type=float, default=0.05, help="Output interval seconds, default 0.05s")
    parser.add_argument("--duration", type=float, default=None, help="Total streaming duration in seconds (stream mode only). If omitted, infinite")
    parser.add_argument("--outfile", type=str, default="output.jsonl", help="Output file path, default output.jsonl")
    args = parser.parse_args()

    output_path = args.outfile

    if args.stream:
        # Streaming: generate sine + noise samples in real time
        freq_hz = 5.0
        phase = 0.0
        start_ts = time.time()
        two_pi = 2.0 * np.pi
        with open(output_path, "w", encoding="utf-8") as fp:
            try:
                while True:
                    if args.duration is not None and (time.time() - start_ts) >= args.duration:
                        break
                    value = float(np.sin(phase) + 0.2 * np.random.randn())
                    record = {"timestamp": iso_utc_now_ms(), "value": value}
                    fp.write(json.dumps(record, ensure_ascii=False) + "\n")
                    fp.flush()

                    time.sleep(args.interval)
                    phase += two_pi * freq_hz * args.interval
                    if phase >= two_pi:
                        # Prevent phase from growing unbounded
                        phase -= two_pi * int(phase / two_pi)
            except KeyboardInterrupt:
                pass
        print(f"saved json lines to {output_path}")
        return

    # One-off: sliding windows over a fixed-length signal, output last sample per window
    with open(output_path, "w", encoding="utf-8") as fp:
        for start in range(0, len(signalTotal)-window_size, step_size):  # slide by step_size samples
            end = start + window_size  # end index of current window
            window_signal = signalTotal[start:end]  # signal segment inside the window
            value = float(window_signal[-1])  # current value: last sample of the window
            record = {"timestamp": iso_utc_now_ms(), "value": value}
            fp.write(json.dumps(record, ensure_ascii=False) + "\n")
            fp.flush()
            time.sleep(0.05)  # similar to prior display frame rate
    print(f"saved json lines to {output_path}")


if __name__ == "__main__":
    main()