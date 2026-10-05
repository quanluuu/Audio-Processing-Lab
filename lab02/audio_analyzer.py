from pathlib import Path
import numpy as np
import sounddevice as sd
import soundfile as sf

def load_audio(file_path: str | Path) -> tuple[np.ndarray, int]:
    """
    Đọc file .wav lên bộ nhớ.
    Trả về một tuple gồm: (mảng dữ liệu âm thanh, tần số lấy mẫu sample_rate)
    """
    target_path = Path(file_path)
    if not target_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file âm thanh tại: {target_path}")
    
    # sf.read trả về (data, sample_rate)
    data, sample_rate = sf.read(target_path)
    return data, sample_rate

def analyze_audio(file_path: str | Path) -> dict:
    """
    Phân tích chi tiết một file âm thanh và trả về một từ điển (dict) chứa các thông số.
    """
    data, sample_rate = load_audio(file_path)

    # 1. Xác định số kênh (Channels)
    # Nếu mảng 1 chiều (ndim == 1) -> Mono (1 kênh)
    # Nếu mảng 2 chiều (ndim == 2) -> Stereo (2 kênh)
    if data.ndim == 1:
        channels = 1
        num_samples = len(data)
    else:
        channels = data.shape[1]
        num_samples = data.shape[0]

    # 2. Tính thời lượng âm thanh (Duration tính bằng giây)
    duration_seconds = num_samples / sample_rate

    # 3. Tính biên độ lớn nhất (Peak Amplitude: từ 0.0 đến 1.0)
    peak_amplitude = float(np.max(np.abs(data)))

    # 4. Tính năng lượng trung bình (RMS - Root Mean Square)
    # RMS càng lớn thì âm thanh càng to, RMS cực nhỏ (< 0.01) nghĩa là khoảng lặng
    rms_energy = float(np.sqrt(np.mean(data**2)))

    # 5. Đánh giá sơ bộ xem đoạn âm thanh có phải là khoảng lặng không
    is_silent = rms_energy < 0.005

    return {
        "file_name": Path(file_path).name,
        "sample_rate": sample_rate,
        "channels": channels,
        "channel_type": "Mono (1 kênh)" if channels == 1 else "Stereo (2 kênh)",
        "num_samples": num_samples,
        "duration_seconds": round(duration_seconds, 2),
        "peak_amplitude": round(peak_amplitude, 4),
        "rms_energy": round(rms_energy, 4),
        "is_silent": is_silent,
        "is_ai_ready": (sample_rate == 16000 and channels == 1)
    }