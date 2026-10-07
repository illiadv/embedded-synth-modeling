import numpy as np
import argparse

def calculate_snr(
    file_path: str,
    sampling_rate: int = 8000,
    f0: float = 220.0,
    max_harmonics: int = 10,
):
    # 1. Load 16-bit signed PCM data
    data = np.fromfile(file_path, dtype=np.int16).astype(np.float64)
    n = len(data)
    if n == 0:
        raise ValueError("The provided file is empty.")

    t = np.arange(n) / sampling_rate

    # 2. Fit 220 Hz reference wave: y(t) = A*cos(w0*t) + B*sin(w0*t) + C (DC)
    omega0 = 2 * np.pi * f0
    design_matrix = np.column_stack(
        [np.cos(omega0 * t), np.sin(omega0 * t), np.ones(n)]
    )
    coeffs, _, _, _ = np.linalg.lstsq(design_matrix, data, rcond=None)
    a1, b1, dc_offset = coeffs

    # Fundamental amplitude and power
    v_fund = np.sqrt(a1**2 + b1**2)
    p_fund = (v_fund**2) / 2.0

    # Fit Harmonics (2*f0, 3*f0, ... up to Nyquist: 4000 Hz)
    nyquist = sampling_rate / 2.0
    k_max = int(min(max_harmonics, nyquist // f0))
    harmonic_powers = []

    for k in range(2, k_max + 1):
        wk = 2 * np.pi * (k * f0)
        h_matrix = np.column_stack([np.cos(wk * t), np.sin(wk * t)])
        h_coeffs, _, _, _ = np.linalg.lstsq(h_matrix, data, rcond=None)
        vk = np.sqrt(h_coeffs[0] ** 2 + h_coeffs[1] ** 2)
        harmonic_powers.append((vk**2) / 2.0)

    p_harmonics = np.sum(harmonic_powers)

    # 4. Noise power (Total AC Power - Fundamental Power - Harmonic Power)
    ac_signal = data - dc_offset
    p_total_ac = np.mean(ac_signal**2)
    p_noise = max(p_total_ac - p_fund - p_harmonics, 1e-12)

    # Compute SNR
    snr_db = 10.0 * np.log10(p_fund / p_noise)
    return snr_db

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)  
    parser.add_argument("--sampling-rate", type=int, required=True)  
    parser.add_argument("--frequency", type=float, required=True)  
    args = parser.parse_args()

    snr = calculate_snr(args.input_file, args.sampling_rate, args.frequency)
    print(f"SNR: {snr:.2f}")

if __name__ == "__main__":
    main()
