"""
Sinh bộ dữ liệu GIẢ LẬP để test notebook Lab 2 (KHÔNG phải giọng thật).

Mỗi "từ" được tổng hợp bằng mô hình nguồn - bộ lọc:
  - âm hữu thanh: chuỗi xung thanh môn (F0) -> các bộ cộng hưởng formant F1, F2, F3
    với quỹ đạo formant thay đổi theo thời gian (mô phỏng nguyên âm / bán nguyên âm / âm mũi)
  - âm vô thanh: nhiễu trắng đã lọc thông cao (mô phỏng /x/ của "kh", /h/)
Mỗi lần lặp có tốc độ nói, âm lượng, F0 và độ dài silence đầu/cuối ngẫu nhiên,
cộng nhiễu nền nhỏ -> đủ biến thiên để thử endpoint detection, MFCC, DTW.

Chạy:  python make_sample_data.py              # tạo dataset/ (người 1)
       python make_sample_data.py --speaker2   # tạo thêm dataset_speaker2/ cho E4
Ghi chú: file bon_05.wav của người 1 được cố ý ghi ở 44.1 kHz stereo để
kiểm tra bước "đưa tất cả file về WAV mono 16 kHz" trong notebook.
"""
import sys
from pathlib import Path
import numpy as np
from scipy.signal import lfilter, resample_poly
from scipy.io import wavfile

FS = 16000


def reson(x, f, bw, fs=FS):
    """Bộ cộng hưởng bậc 2 tại tần số f (Hz), băng thông bw (Hz)."""
    r = np.exp(-np.pi * bw / fs)
    th = 2 * np.pi * f / fs
    return lfilter([1 - r], [1, -2 * r * np.cos(th), r * r], x)


def voiced(rng, dur, f1s, f2s, f0s, amp=1.0, f3=2600):
    n = int(dur * FS)
    f0 = np.interp(np.arange(n), [0, n - 1], f0s) * (1 + 0.01 * rng.standard_normal())
    ph = np.cumsum(f0 / FS)
    src = (np.diff(np.floor(ph), prepend=0) > 0).astype(float)      # xung thanh môn
    src = lfilter([1], [1, -0.95], src)                              # tilt phổ nguồn
    F1 = np.interp(np.arange(n), np.linspace(0, n - 1, len(f1s)), f1s)
    F2 = np.interp(np.arange(n), np.linspace(0, n - 1, len(f2s)), f2s)
    out = np.zeros(n)
    seg = 160
    for s in range(0, n, seg):                                       # formant thay đổi theo từng 10 ms
        e = min(n, s + seg + 200)
        x = src[s:e]
        y = reson(x, F1[s], 80) + 0.6 * reson(x, F2[s], 120) + 0.2 * reson(x, f3, 200)
        out[s:min(n, s + seg)] += y[:min(n, s + seg) - s]
    out = lfilter([1, -1], [1, -0.99], out)                          # bỏ DC
    env = np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / (0.02 * FS))
    return amp * out * env


def noise(rng, dur, amp=0.15):
    n = int(dur * FS)
    x = lfilter([1, -0.9], [1], rng.standard_normal(n))              # nhiễu thiên tần số cao
    env = np.minimum(1, np.minimum(np.arange(n), n - np.arange(n)) / (0.01 * FS))
    return amp * x * env


# s = hệ số tốc độ nói, p = hệ số cao độ (người nói)
WORDS = {
    # "không": /x/ xát vô thanh + nguyên âm tròn môi /o/ + âm mũi /ŋ/
    "khong": lambda r, s, p: [noise(r, 0.09 * s, 0.04),
                              voiced(r, 0.30 * s, [500, 450, 350], [900, 850, 1000], [120 * p, 120 * p])],
    # "một": âm mũi /m/ + /o/ ngắn, thanh nặng (F0 rơi), tắc cuối /t/
    "mot":   lambda r, s, p: [voiced(r, 0.06 * s, [300, 300], [1100, 1100], [115 * p, 110 * p], 0.4),
                              voiced(r, 0.18 * s, [500, 450], [900, 900], [110 * p, 95 * p])],
    # "hai": /h/ + /a/ trượt sang /i/
    "hai":   lambda r, s, p: [noise(r, 0.06 * s, 0.03),
                              voiced(r, 0.32 * s, [750, 700, 350], [1300, 1600, 2200], [125 * p, 125 * p])],
    # "ba": tắc /b/ + /a/ dài
    "ba":    lambda r, s, p: [voiced(r, 0.03 * s, [300, 300], [1000, 1000], [125 * p, 125 * p], 0.3),
                              voiced(r, 0.32 * s, [780, 780], [1250, 1250], [125 * p, 125 * p])],
    # "bốn": /b/ + /o/ + /n/, thanh sắc (F0 lên)
    "bon":   lambda r, s, p: [voiced(r, 0.03 * s, [300, 300], [1000, 1000], [140 * p, 140 * p], 0.3),
                              voiced(r, 0.30 * s, [480, 470, 300], [900, 900, 1500], [130 * p, 170 * p])],
}


def make(root, seed=0, pitch=1.0, n_rep=5, odd_format_file=None):
    rng = np.random.default_rng(seed)
    root = Path(root)
    for w, fn in WORDS.items():
        for k in range(1, n_rep + 1):
            s = rng.uniform(0.8, 1.25)                               # tốc độ nói
            sig = np.concatenate(fn(rng, s, pitch))
            sig = sig / np.abs(sig).max() * rng.uniform(0.4, 0.8)    # âm lượng
            pre = np.zeros(int(rng.uniform(0.2, 0.45) * FS))         # silence 0.2-0.45 s
            post = np.zeros(int(rng.uniform(0.2, 0.45) * FS))
            y = np.concatenate([pre, sig, post])
            y = y + 0.002 * rng.standard_normal(len(y))              # nhiễu nền
            p = root / w / f"{w}_{k:02d}.wav"
            p.parent.mkdir(parents=True, exist_ok=True)
            if odd_format_file == p.name:                            # 44.1 kHz stereo để test chuyển đổi
                y44 = resample_poly(y, 441, 160)
                st = np.stack([y44, 0.9 * y44], axis=1)
                wavfile.write(p, 44100, (st * 32767).astype(np.int16))
            else:
                wavfile.write(p, FS, (y * 32767).astype(np.int16))
    print(f"Đã tạo {len(WORDS) * n_rep} file trong {root.resolve()}")


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    make(here / "dataset", seed=0, pitch=1.0, odd_format_file="bon_05.wav")
    if "--speaker2" in sys.argv:
        make(here / "dataset_speaker2", seed=7, pitch=1.6)          # "người 2": giọng cao hơn
