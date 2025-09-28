import os
import json
import time
from collections import deque
import numpy as np
import streamlit as st
from datetime import datetime
from ai_handler import get_ai_handler
import pandas as pd
import altair as alt


st.set_page_config(page_title="Signal Insights", page_icon="📈", layout="wide")

DATA_JSON_PATH = "Trible_EXG_Signal1.json"

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


def load_signal1_from_json(filepath: str) -> tuple[list[float], list[float]]:
    """Load Time and Signal1 arrays from a JSON file with structure:
    {
      "Segment": 1,
      "Message": "...",
      "Time": [ ... ],
      "Signal1": [ ... ],
      "Signal2": [ ... ],
      "Signal3": [ ... ]
    }

    Returns (time_list, signal1_list). If Time is missing or invalid,
    a simple index [0..N-1] will be used for the x-axis.
    """
    time_list: list[float] = []
    signal_list: list[float] = []
    if not os.path.exists(filepath):
        return time_list, signal_list
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        raw_times = data.get("Time")
        raw_values = data.get("Signal1")
        if isinstance(raw_values, list):
            # Convert to floats where possible
            try:
                signal_list = [float(v) for v in raw_values]
            except (TypeError, ValueError):
                signal_list = []
        if isinstance(raw_times, list) and len(raw_times) == len(signal_list):
            try:
                time_list = [float(t) for t in raw_times]
            except (TypeError, ValueError):
                time_list = list(range(len(signal_list)))
        else:
            time_list = list(range(len(signal_list)))
    except (OSError, json.JSONDecodeError):
        return [], []
    return time_list, signal_list

def load_signal2_from_json(filepath: str) -> tuple[list[float], list[float]]:
    """Load Time and Signal2 arrays from a JSON file with structure:
    {
      "Segment": 1,
      "Message": "...",
      "Time": [ ... ],
      "Signal1": [ ... ],
      "Signal2": [ ... ],
      "Signal3": [ ... ]
    }

    Returns (time_list, signal2_list). If Time is missing or invalid,
    a simple index [0..N-1] will be used for the x-axis.
    """
    time_list: list[float] = []
    signal_list: list[float] = []
    if not os.path.exists(filepath):
        return time_list, signal_list
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        raw_times = data.get("Time")
        raw_values = data.get("Signal2")
        if isinstance(raw_values, list):
            # Convert to floats where possible
            try:
                signal_list = [float(v) for v in raw_values]
            except (TypeError, ValueError):
                signal_list = []
        if isinstance(raw_times, list) and len(raw_times) == len(signal_list):
            try:
                time_list = [float(t) for t in raw_times]
            except (TypeError, ValueError):
                time_list = list(range(len(signal_list)))
        else:
            time_list = list(range(len(signal_list)))
    except (OSError, json.JSONDecodeError):
        return [], []
    return time_list, signal_list
def load_signal3_from_json(filepath: str) -> tuple[list[float], list[float]]:
    """Load Time and Signal1 arrays from a JSON file with structure:
    {
      "Segment": 1,
      "Message": "...",
      "Time": [ ... ],
      "Signal1": [ ... ],
      "Signal2": [ ... ],
      "Signal3": [ ... ]
    }

    Returns (time_list, signal1_list). If Time is missing or invalid,
    a simple index [0..N-1] will be used for the x-axis.
    """
    time_list: list[float] = []
    signal_list: list[float] = []
    if not os.path.exists(filepath):
        return time_list, signal_list
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        raw_times = data.get("Time")
        raw_values = data.get("Signal3")
        if isinstance(raw_values, list):
            # Convert to floats where possible
            try:
                signal_list = [float(v) for v in raw_values]
            except (TypeError, ValueError):
                signal_list = []
        if isinstance(raw_times, list) and len(raw_times) == len(signal_list):
            try:
                time_list = [float(t) for t in raw_times]
            except (TypeError, ValueError):
                time_list = list(range(len(signal_list)))
        else:
            time_list = list(range(len(signal_list)))
    except (OSError, json.JSONDecodeError):
        return [], []
    return time_list, signal_list


def load_message_from_json(filepath: str) -> str:
    """Load the 'Message' field from the given JSON file. Returns empty string if missing."""
    if not os.path.exists(filepath):
        return ""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        msg = data.get("Message")
        return str(msg) if msg is not None else ""
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return ""

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
        exg_time1, exg_values1 = load_signal1_from_json(DATA_JSON_PATH)
        if exg_values1:
            # Use provided Time if valid; otherwise fallback to index
            x_vals = exg_time1 if exg_time1 else list(range(len(exg_values1)))
            df_plot = pd.DataFrame({"x": x_vals, "y": exg_values1})
            chart = (
                alt.Chart(df_plot)
                .mark_line(color="#1f77b4")
                .encode(
                    x=alt.X("x:Q", title="Time"),
                    y=alt.Y("y:Q", title="Signal1", scale=alt.Scale(domain=[2.4, 2.45])),
                )
                .properties(height=320)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info(f"No data found in {DATA_JSON_PATH} or 'Signal1' missing.")
            
        # Add Signal2 chart under Signal1
        # exg_time2, exg_values2 = load_signal2_from_json("Trible_EXG_Signal1.json")
        # if exg_values2:
        #     x2 = exg_time2 if exg_time2 else list(range(len(exg_values2)))
        #     df2 = pd.DataFrame({"x": x2, "y": exg_values2})
        #     chart2 = (
        #         alt.Chart(df2)
        #         .mark_line(color="#E28312")
        #         .encode(
        #             x=alt.X("x:Q", title="Time"),
        #             y=alt.Y("y:Q", title="Signal2", scale=alt.Scale(domain=[2.0, 4.0])),
        #         )
        #         .properties(height=320)
        #     )
        #     st.altair_chart(chart2, use_container_width=True)
        # else:
        #     st.info("No data found in Trible_EXG_Signal1.json or 'Signal2' missing.")

        # Add Signal2 chart under Signal1
        exg_time2, exg_values2 = load_signal2_from_json(DATA_JSON_PATH)
        if exg_values2:
            x2 = exg_time2 if exg_time2 else list(range(len(exg_values2)))
            df2 = pd.DataFrame({"x": x2, "y": exg_values2})
            chart2 = (
                alt.Chart(df2)
                .mark_line(color="#E28312")
                .encode(
                    x=alt.X("x:Q", title="Time"),
                    y=alt.Y("y:Q", title="Signal2"),
                )
                .properties(height=320)
            )
            st.altair_chart(chart2, use_container_width=True)
        else:
            st.info(f"No data found in {DATA_JSON_PATH} or 'Signal2' missing.")

        # Add Signal3 chart under Signal2
        exg_time3, exg_values3 = load_signal3_from_json(DATA_JSON_PATH)
        if exg_values3:
            x3 = exg_time3 if exg_time3 else list(range(len(exg_values3)))
            df3 = pd.DataFrame({"x": x3, "y": exg_values3})
            chart3 = (
                alt.Chart(df3)
                .mark_line(color="#2ca02c")
                .encode(
                    x=alt.X("x:Q", title="Time"),
                    y=alt.Y("y:Q", title="Signal3"),
                )
                .properties(height=320)
            )
            st.altair_chart(chart3, use_container_width=True)
        else:
            st.info(f"No data found in {DATA_JSON_PATH} or 'Signal3' missing.")
        
        

        # st.markdown("**Textual Explanation**")
        # if values:
        #     # estimate sample rate from timestamps (median delta)
        #     sr_est = 1.0
        #     if len(times) > 1:
        #         deltas = np.diff(np.array([t.timestamp() for t in times], dtype=float))
        #         deltas = deltas[deltas > 0]
        #         if deltas.size > 0:
        #             dt = float(np.median(deltas))
        #             if dt > 0:
        #                 sr_est = 1.0 / dt
        #     sig_arr = np.array(values, dtype=float)
        #     metrics = compute_metrics(sig_arr, int(sr_est) if sr_est > 0 else 1)
        #     st.text(format_metrics_text(metrics))
        # else:
        #     st.info("No data to compute metrics. Please generate output.jsonl.")

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
        msg = load_message_from_json(DATA_JSON_PATH)
        ai_explanation = msg if msg else f"No message found in {DATA_JSON_PATH}"
        st.markdown(ai_explanation)


    # section 3: model recommendation
    with col_ai:
        st.markdown("**AI Suggestions**")
        # ai_suggestions = "Fake data"
        # st.markdown(ai_suggestions)
        prompt_default = (
            "Based on the following signal metrics, provide concise, actionable suggestions. "
            "Cover likely signal sources, whether filtering is needed, threshold ideas, and next steps."
        )
        user_prompt = st.text_area("Optional: Ask AI to give you more personalized advice", height=120)
        if st.button("Generate Suggestions", type="primary", use_container_width=True):
            ai_handler = get_ai_handler()
            system = (
                "You are a health and fitness AI assistant. Based on the current health status and suggestions provided, "
                "answer the user's question with personalized advice. Be helpful, encouraging, and health-focused. "
                "Provide practical recommendations in a friendly tone."
            )
            
            # Use the predefined explanation and suggestions as context
            context_info = (
                f"Current Health Status: {ai_explanation}\n"
                # f"Current Recommendations: {ai_suggestions}\n"
                f"Signal Data: {format_metrics_text(metrics) if 'metrics' in locals() and metrics else 'No signal data available'}\n"
                f"User Question: {user_prompt.strip() if user_prompt else 'General health advice request'}"
            )
            
            messages = [
                {"role": "system", "content": system},
                {
                    "role": "user", 
                    "content": context_info
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


