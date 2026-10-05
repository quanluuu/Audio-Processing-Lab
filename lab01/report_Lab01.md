# BÁO CÁO THỰC HÀNH LAB 1: PHÂN TÍCH VÀ XỬ LÝ TÍN HIỆU ÂM THANH SỐ
**Học phần:** CSE457 - Xử lý Âm thanh và Tiếng nói  
**Ngày thực hiện:** 21/09/2026  
**Thư mục lưu bài:** `Lab01_MSSV_HoTen/`  

---

## 1. TỔNG QUAN FILE ÂM THANH ĐẦU VÀO
- **Đường dẫn tệp gốc:** `audio/input/the_quick_brown_fox_male_female.mp3`
- **Tần số lấy mẫu ($F_s$):** $22,050\text{ Hz}$ (Tần số Nyquist $F_{\text{Nyquist}} = 11,025\text{ Hz}$)
- **Số kênh (Channels):** $1\text{ (Mono)}$
- **Thời lượng (Duration):** $6.632\text{ s}$
- **Độ rộng mẫu (Sample Width):** $2\text{ bytes (16-bit PCM equivalent)}$
- **Giá trị đỉnh biên độ (Peak):** $0.7807\text{ (Không bị clipping)}$
- **Mức năng lượng RMS:** $0.0931\text{ (-20.62 dBFS)}$

---

## 2. KẾT QUẢ VÀ NHẬN XÉT CÁC NỘI DUNG THỰC HÀNH

### A. Đọc & Chuẩn hóa Dữ liệu Âm thanh
Dữ liệu âm thanh được tải bằng thư viện `librosa`/`soundfile` và chuẩn hóa về dải biên độ $[-1.0, 1.0]$. Giá trị đỉnh $Peak = 0.7807 < 1.0$ cho thấy tín hiệu âm thanh đạt chất lượng tốt, không bị vỡ tiếng hoặc clipping.

### B. Phân tích Miền Thời gian (Time-Domain Analysis)
- **Đồ thị Waveform:** Hiển thị rõ cấu trúc biến đổi biên độ của các từ trong câu nói "The quick brown fox...".
- **So sánh 2 đoạn đặc trưng:**
  - *Đoạn 1 (Voiced - Nguyên âm hữu thanh, 0.5s - 1.5s):* Biên độ đỉnh $Peak = 0.7807$, $RMS = -18.25\text{ dBFS}$, Năng lượng $E = 217.15$. Đồ thị Zoom hiển thị các xung thanh môn lặp lại chu kỳ $T_0 \approx 8.3\text{ ms}$ (tần số cơ bản $F_0 \approx 120\text{ Hz}$).
  - *Đoạn 2 (Unvoiced - Âm vô thanh/Khoảng lặng, 2.5s - 3.5s):* Biên độ đỉnh $Peak = 0.5970$, $RMS = -23.02\text{ dBFS}$, Năng lượng $E = 109.90$.

### C. Phân tích Miền Tần số bằng FFT (Frequency-Domain Analysis)
- **Cấu trúc đỉnh phổ (Harmonics):** Phổ biên độ FFT đoạn âm hữu thanh (sau khi nhân cửa sổ Hamming) cho thấy các đỉnh phổ nổi bật xuất hiện tại tần số cơ bản $F_0$ và các họa âm liên tiếp (Harmonic series).
- **So sánh NFFT ($NFFT=2048$ vs $NFFT=65536$):**
  - Tăng NFFT từ $2048$ lên $65536$ làm giảm khoảng cách giữa các bin tần số $\Delta f = F_s / NFFT$ từ $10.77\text{ Hz}$ xuống $0.34\text{ Hz}$, giúp đường cong đồ thị mịn hơn.
  - Tuy nhiên, **độ phân giải vật lý thực (True Physical Resolution)** không thay đổi ($\Delta f_{\text{true}} \approx F_s / L = 1.00\text{ Hz}$), hoàn toàn do độ dài khung thời gian $L = 1.0\text{ s}$ quyết định.

### D. Phân tích STFT và Spectrogram
Thực nghiệm so sánh 3 độ dài khung (Frame length $10\text{ ms}$, $25\text{ ms}$, $50\text{ ms}$) với hop size $10\text{ ms}$:
- **Khung ngắn $10\text{ ms}$:** Độ phân giải thời gian cao (thấy rõ dải dọc transient), nhưng độ phân giải tần số bị mờ.
- **Khung dài $50\text{ ms}$:** Độ phân giải tần số cao (hiển thị rõ đường formant ngang), nhưng thời gian bị nhòe (time smearing).
- **Khung chuẩn $25\text{ ms}$:** Cân bằng tối ưu giữa miền thời gian và tần số.

### E. Thí nghiệm Cửa sổ (Windowing: Rectangular vs Hamming)
- **Rectangular Window:** Búp sóng bên cao (chỉ suy hao $-13\text{ dB}$), gây rò rỉ phổ mạnh (spectral leakage) làm sàn nhiễu phổ nhấc lên mức $-35\text{ dB}$.
- **Hamming Window:** Triệt tiêu biên độ ở 2 mép khung, giảm búp sóng bên xuống $-43\text{ dB}$, hạ sàn nhiễu phổ xuống dưới $-60\text{ dB}$.

### F. Lọc Số (Digital FIR Filtering)
- **Low-pass FIR (fc = 2 kHz, 201 taps):** Triệt tiêu dải tần trên $2000\text{ Hz}$. Âm thanh trong `audio/filtered_lpf_2kHz.wav` trở nên trầm tối (muffled).
- **High-pass FIR (fc = 3 kHz, 201 taps):** Loại bỏ toàn bộ tần số thấp và giọng nền. Âm thanh trong `audio/filtered_hpf_3kHz.wav` chỉ còn tiếng xì của phụ âm.
- **Bù trễ nhóm:** Đã bù trễ $100\text{ mẫu}$ ($\approx 4.54\text{ ms}$) giúp tín hiệu khớp chính xác về pha.

### G. Lượng tử hóa, Resampling & Mã hóa
- **SNR Lượng tử:** SNR đo được tăng tuyến tính $\approx 6\text{ dB/bit}$ theo đúng công thức $SNR \approx 6.02B + 4.77\text{ dB}$ (đạt $14.1\text{ dB}$ ở 4-bit, $39.1\text{ dB}$ ở 8-bit và $86.5\text{ dB}$ ở 16-bit).
- **Resampling (16 kHz & 8 kHz):** Hạ tần số lấy mẫu về $8\text{ kHz}$ giữ tiếng nói vẫn nghe rõ, đạt tiêu chuẩn đường truyền thoại (Telephony).
- **Mã hóa MP3 vs PCM:** MP3 nén đạt tỷ lệ $comp\_ratio \approx 6.37 : 1$, tiết kiệm $84.3\%$ dung lượng so với PCM 16-bit Mono.

---

## 3. CÂU HỎI BÁO CÁO LÝ THUYẾT (MỤC 6)

1. **Nyquist Rate:** $F_s = 44.1\text{ kHz}$ chỉ biểu diễn độc lập đến $22.05\text{ kHz}$ vì tần số Nyquist $F_{\text{Nyquist}} = F_s / 2 = 22.05\text{ kHz}$. Các tần số $f > 22.05\text{ kHz}$ bị dội ngược (aliasing) về dải $[0, 22.05\text{ kHz}]$.
2. **NFFT 2048 vs 8192:** Tăng NFFT chỉ làm khoảng cách bin tần số $\Delta f = F_s / NFFT$ nhỏ hơn (mịn hơn do zero-padding), còn độ phân giải thực $\Delta f_{\text{true}} \approx F_s / L$ không đổi nếu độ dài khung $L = 25\text{ ms}$ giữ nguyên.
3. **Hamming vs Rectangular:** Hamming triệt tiêu 2 mép khung làm búp sóng bên giảm xuống $-43\text{ dB}$ (giảm rò rỉ phổ), nhưng búp sóng chính rộng gấp đôi làm các đỉnh gần nhau khó phân tách hơn.
4. **Group Delay FIR 201 taps:** Độ trễ $\tau = (201-1)/2 = 100\text{ mẫu} \approx 2.27\text{ ms}$ tại $44.1\text{ kHz}$. Độ trễ này rất nhỏ và không ảnh hưởng trong ứng dụng thời gian thực.
5. **Giảm biên độ đầu vào & SNR:** Giảm $\sigma_x$ làm giảm công suất tín hiệu $P_x$, trong khi công suất nhiễu lượng tử $P_e = \Delta^2/12$ giữ nguyên. Do đó tỷ số $SNR_Q = 10\log_{10}(P_x/P_e)$ bị sụt giảm.
6. **Kích thước PCM 60s:** PCM 16-bit stereo 44.1 kHz trong 60s có kích thước $\approx 10.09\text{ MB}$. MP3 128 kbps có kích thước $\approx 0.915\text{ MB}$ (PCM gấp $\approx 11.03$ lần MP3).
7. **"Nghe tốt hơn" không đồng nghĩa "SNR lớn hơn":**
   - *LPF khử nhiễu cao tần:* Cắt bớt dải cao giúp nghe bớt rít êm tai hơn nhưng công suất sai số tăng làm SNR giảm.
   - *Mã hóa MP3:* Khai thác Auditory Masking giấu nhiễu dưới ngưỡng nghe làm SNR đo được không cao nhưng cảm nhận âm thanh vẫn trung thực.
