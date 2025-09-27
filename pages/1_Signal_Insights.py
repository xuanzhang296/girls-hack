import os
import json
import time
from collections import deque
import numpy as np
import streamlit as st
from datetime import datetime
from ai_handler import get_ai_handler


st.set_page_config(page_title="Signal Insights", page_icon="📈", layout="wide")


def generate_signal(sample_rate_hz: int, duration_s: float, freq_hz: float, noise_std: float) -> tuple[np.ndarray, np.ndarray]:
    num_samples = int(sample_rate_hz * duration_s)
    t = np.linspace(0, duration_s, num_samples, endpoint=False)
    clean = np.sin(2 * np.pi * freq_hz * t)
    noise = np.random.normal(0.0, noise_std, size=num_samples)
    signal = clean + noise
    return t, signal


def compute_metrics(signal: np.ndarray, sample_rate_hz: int) -> dict:
    mean_val = float(np.mean(signal))
    std_val = float(np.std(signal))
    peak_to_peak = float(np.max(signal) - np.min(signal))
    rms = float(np.sqrt(np.mean(np.square(signal))))
    # simple dominant freq via FFT
    freqs = np.fft.rfftfreq(len(signal), d=1.0 / sample_rate_hz)
    spectrum = np.abs(np.fft.rfft(signal))
    dom_idx = int(np.argmax(spectrum[1:]) + 1) if len(spectrum) > 1 else 0
    dominant_freq_hz = float(freqs[dom_idx]) if dom_idx < len(freqs) else 0.0
    return {
        "mean": mean_val,
        "std": std_val,
        "peak_to_peak": peak_to_peak,
        "rms": rms,
        "dominant_freq_hz": dominant_freq_hz,
    }


def format_metrics_text(metrics: dict) -> str:
    return (
        f"Signal Statistics\n"
        f"- Mean: {metrics['mean']:.4f}\n"
        f"- Std Dev: {metrics['std']:.4f}\n"
        f"- Peak-to-Peak: {metrics['peak_to_peak']:.4f}\n"
        f"- RMS: {metrics['rms']:.4f}\n"
        f"- Dominant Freq: {metrics['dominant_freq_hz']:.2f} Hz\n"
    )


def load_first_n_jsonl(filepath: str, n: int = 100) -> tuple[list[datetime], list[float]]:
    times: list[datetime] = []
    values: list[float] = []
    if not os.path.exists(filepath):
        return times, values
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if count >= n:
                break
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                ts_raw = obj.get("timestamp")
                val_raw = obj.get("value")
                if ts_raw is None or val_raw is None:
                    continue
                ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
                val = float(val_raw)
                times.append(ts)
                values.append(val)
                count += 1
            except (json.JSONDecodeError, ValueError, TypeError):
                continue
    return times, values


def load_last_n_jsonl(filepath: str, n: int = 100) -> tuple[list[datetime], list[float]]:
    times: list[datetime] = []
    values: list[float] = []
    if not os.path.exists(filepath) or n <= 0:
        return times, values
    buffer: deque[str] = deque(maxlen=n)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    buffer.append(line)
    except OSError:
        return times, values
    for line in buffer:
        try:
            obj = json.loads(line)
            ts_raw = obj.get("timestamp")
            val_raw = obj.get("value")
            if ts_raw is None or val_raw is None:
                continue
            ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
            val = float(val_raw)
            times.append(ts)
            values.append(val)
        except (json.JSONDecodeError, ValueError, TypeError):
            continue
    return times, values


def main() -> None:
    st.markdown("#### Signal Insights")

    with st.sidebar:
        st.markdown("**Signal Parameters**")
        sample_rate = st.slider("Sample Rate (Hz)", 100, 5000, 1000, step=100)
        duration = st.slider("Duration (s)", 1, 20, 5)
        base_freq = st.slider("Base Frequency (Hz)", 1, 50, 5)
        noise_std = st.slider("Noise Std Dev", 0.0, 1.0, 0.2, step=0.05)

    # Load latest data once (shared by chart and textual explanation)
    times, values = load_last_n_jsonl("output.jsonl", n=100)

    # layout: three columns
    col_chart, col_text, col_ai = st.columns([2, 1.2, 1.6], gap="large")

    # section 1: line chart
    with col_chart:
        st.markdown("**Signal Plot**")
        if times and values:
            st.line_chart({"time": times, "value": values}, x="time", y="value", height=320)
        else:
            st.info("No data found in output.jsonl. Please generate data first.")

        st.markdown("**Textual Explanation**")
        if values:
            # estimate sample rate from timestamps (median delta)
            sr_est = 1.0
            if len(times) > 1:
                deltas = np.diff(np.array([t.timestamp() for t in times], dtype=float))
                deltas = deltas[deltas > 0]
                if deltas.size > 0:
                    dt = float(np.median(deltas))
                    if dt > 0:
                        sr_est = 1.0 / dt
            sig_arr = np.array(values, dtype=float)
            metrics = compute_metrics(sig_arr, int(sr_est) if sr_est > 0 else 1)
            st.text(format_metrics_text(metrics))
        else:
            st.info("No data to compute metrics. Please generate output.jsonl.")

    # section 2: textual explanation
    # with col_text:
    #     st.markdown("**Textual Explanation**")
    #     if values:
    #         # estimate sample rate from timestamps (median delta)
    #         sr_est = 1.0
    #         if len(times) > 1:
    #             deltas = np.diff(np.array([t.timestamp() for t in times], dtype=float))
    #             deltas = deltas[deltas > 0]
    #             if deltas.size > 0:
    #                 dt = float(np.median(deltas))
    #                 if dt > 0:
    #                     sr_est = 1.0 / dt
    #         sig_arr = np.array(values, dtype=float)
    #         metrics = compute_metrics(sig_arr, int(sr_est) if sr_est > 0 else 1)
    #         st.text(format_metrics_text(metrics))
    #     else:
    #         st.info("No data to compute metrics. Please generate output.jsonl.")
    # section 2: textual explanation
    with col_text:
        st.markdown("**Textual Explanation**")
        st.markdown("你现在心跳加速， 呼吸急促，脂肪燃烧")


    # section 3: model recommendation
    with col_ai:
        st.markdown("**AI Suggestions**")
        st.markdown("建议你减少运动 多吃好吃的， 这样你能长命百岁！！！！")
        prompt_default = (
            "Based on the following signal metrics, provide concise, actionable suggestions. "
            "Cover likely signal sources, whether filtering is needed, threshold ideas, and next steps."
        )
        user_prompt = st.text_area("Optional: Ask AI to give you more personalized advice", height=120)
        if st.button("Generate Suggestions", type="primary", use_container_width=True):
            ai_handler = get_ai_handler()
            system = (
                "You are a senior signal processing engineer. Turn statistics into engineering advice. "
                "Be structured. Provide up to 6 bullet points, each under 30 words."
            )
            messages = [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": (
                        f"Metrics: {format_metrics_text(metrics)}\n"
                        f"Sample Rate: {sample_rate} Hz, Duration: {duration} s, Base Freq: {base_freq} Hz, Noise σ: {noise_std}\n"
                        f"Context: {user_prompt.strip() if user_prompt else 'None'}"
                    ),
                },
            ]
            # stream response via handler
            ai_handler.get_ai_response(messages, stream=True)

    st.caption(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Auto-refresh every second to reflect new data points appended to output.jsonl
    time.sleep(0.1)
    st.rerun()


if __name__ == "__main__":
    main()


