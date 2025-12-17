"""VPU 冲击声检测 + 可视化（轻量版）。"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

# 基本参数，可按需修改
AUDIO_PATH = Path(__file__).resolve().parent / "out.wav"
CHANNEL_INDEX = 4
DC_WINDOW_MS = 40.0
SHORT_MS = 6.0
LONG_MS = 60.0
RATIO_THRESHOLD = 3.0
MIN_DURATION_MS = 8.0
MIN_GAP_MS = 35.0


def moving_average(x: np.ndarray, window: int) -> np.ndarray:
    if window <= 1:
        return x
    kernel = np.ones(window, dtype=np.float64) / window
    return np.convolve(x, kernel, mode="same")


def preprocess(signal: np.ndarray, sr: int) -> np.ndarray:
    dc_window = max(int(sr * DC_WINDOW_MS / 1000.0), 1)
    return signal - moving_average(signal, dc_window)


def ratio_score(signal: np.ndarray, sr: int) -> np.ndarray:
    short = max(int(sr * SHORT_MS / 1000.0), 1)
    long = max(int(sr * LONG_MS / 1000.0), 1)
    short_env = moving_average(np.abs(signal), short)
    long_env = moving_average(np.abs(signal), long)
    return short_env / np.maximum(long_env, 1e-6)


def detect_events(mask: np.ndarray, sr: int) -> List[Tuple[float, float]]:
    min_samples = max(int(sr * MIN_DURATION_MS / 1000.0), 1)
    gap_samples = max(int(sr * MIN_GAP_MS / 1000.0), 1)

    events: List[Tuple[int, int]] = []
    start = -1
    for idx, active in enumerate(mask):
        if active and start < 0:
            start = idx
        elif not active and start >= 0:
            if idx - start >= min_samples:
                events = _append_or_merge(events, start, idx, gap_samples)
            start = -1

    if start >= 0 and len(mask) - start >= min_samples:
        events = _append_or_merge(events, start, len(mask), gap_samples)

    return [(s / sr, e / sr) for s, e in events]


def _append_or_merge(events: List[Tuple[int, int]], start: int, end: int, gap: int) -> List[Tuple[int, int]]:
    if events and start - events[-1][1] <= gap:
        previous_start, _ = events[-1]
        events[-1] = (previous_start, end)
    else:
        events.append((start, end))
    return events


def plot_detection(time: np.ndarray, signal: np.ndarray, score: np.ndarray, events: List[Tuple[float, float]]) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)

    axes[0].plot(time, signal, color="steelblue", linewidth=0.8)
    axes[0].set_ylabel("Amplitude")
    axes[0].set_title("VPU 信号与冲击事件")

    axes[1].plot(time, score, color="crimson", linewidth=0.8)
    axes[1].axhline(RATIO_THRESHOLD, color="gray", linestyle="--", linewidth=0.8, label="阈值")
    axes[1].set_ylabel("短/长包络比")
    axes[1].set_xlabel("时间 (s)")
    axes[1].legend(loc="upper right")

    for axis in axes:
        for start, end in events:
            axis.axvspan(start, end, color="lime", alpha=0.25)
        axis.grid(alpha=0.2)

    fig.tight_layout()
    plt.savefig('./impact_noise_rejection.png')


def main() -> None:
    if not AUDIO_PATH.exists():
        raise FileNotFoundError(f"找不到音频文件: {AUDIO_PATH}")

    data, sr = sf.read(AUDIO_PATH, always_2d=True)
    if CHANNEL_INDEX >= data.shape[1]:
        raise ValueError(f"音频仅有 {data.shape[1]} 通道，无法访问 VPU 通道 {CHANNEL_INDEX}")

    signal = data[:, CHANNEL_INDEX].astype(np.float64)
    signal = preprocess(signal, sr)
    score = ratio_score(signal, sr)
    events = detect_events(score > RATIO_THRESHOLD, sr)

    if events:
        print("检测到的冲击事件：")
        for start, end in events:
            print(f"  起始 {start:.3f}s  结束 {end:.3f}s  持续 {(end-start)*1000:.1f}ms")
    else:
        print("未检测到明显的冲击事件。")

    time_axis = np.arange(len(signal)) / sr
    plot_detection(time_axis, signal, score, events)


if __name__ == "__main__":
    main()