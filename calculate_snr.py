import numpy as np
import argparse

def calculate_audio_metrics(
    file_path: str = "waveform_dump.bin",
    sampling_rate: int = 8000,
    f0: float = 220.0,
    num_harmonics: int = 5
) -> dict:
    # 1. Load 16-bit signed PCM data
    data = np.fromfile(file_path, dtype=np.int16).astype(np.float64)
    n = len(data)
    if n == 0:
        raise ValueError("The provided file is empty.")

    # 2. Create time vector and fundamental angular frequency
    t = np.arange(n) / sampling_rate
    omega = 2 * np.pi * f0

    # 3. Build the expanded design matrix
    columns = []

    # Add Fundamental (f0)
    columns.extend([np.sin(omega * t), np.cos(omega * t)])

    # Add Harmonics (2f0, 3f0, ... up to num_harmonics)
    nyquist_limit = sampling_rate / 2.0
    valid_harmonics = []

    for h in range(2, num_harmonics + 1):
        if h * f0 >= nyquist_limit:
            break  # Stop adding harmonics if they exceed the Nyquist frequency (aliasing)
        columns.extend([np.sin(h * omega * t), np.cos(h * omega * t)])
        valid_harmonics.append(h)

    # Add DC Offset column
    columns.append(np.ones(n))

    # Combine into final matrix X
    X = np.column_stack(columns)

    # 4. Solve for all coefficients simultaneously
    coeffs, _, _, _ = np.linalg.lstsq(X, data, rcond=None)

    # 5. Reconstruct the separated signals
    # Fundamental is in the first two columns
    fundamental_signal = coeffs[0] * columns[0] + coeffs[1] * columns[1]
    p_fundamental = np.mean(fundamental_signal**2)

    # Harmonics are in the subsequent columns (in pairs)
    harmonic_signal = np.zeros(n)
    col_idx = 2
    for _ in valid_harmonics:
        harmonic_signal += coeffs[col_idx] * columns[col_idx] + coeffs[col_idx+1] * columns[col_idx+1]
        col_idx += 2
    p_harmonics = np.mean(harmonic_signal**2)

    # DC Offset is the last coefficient
    dc_offset = coeffs[-1]

    # Noise is whatever is left over after subtracting the fundamental, harmonics, and DC
    total_fit = fundamental_signal + harmonic_signal + dc_offset
    noise_signal = data - total_fit
    p_noise = np.mean(noise_signal**2)

    # 6. Calculate final metrics
    snr_db = 10 * np.log10(p_fundamental / p_noise) if p_noise > 0 else float('inf')

    # THD is often represented both in dB and as a percentage
    thd_db = 10 * np.log10(p_harmonics / p_fundamental) if p_harmonics > 0 else float('-inf')
    thd_percent = 100 * np.sqrt(p_harmonics / p_fundamental) if p_fundamental > 0 else 0.0

    # THD+N (SINAD) compares the fundamental to the sum of noise and harmonics
    thdn_db = 10 * np.log10(p_fundamental / (p_noise + p_harmonics)) if (p_noise + p_harmonics) > 0 else float('inf')

    return {
        "SNR_dB": snr_db,
        "THD_dB": thd_db,
        "THD_percent": thd_percent,
        "THD+N_dB": thdn_db,
        "DC_Offset": dc_offset,
        "Harmonics_Analyzed": len(valid_harmonics)
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)  
    parser.add_argument("--sampling-rate", type=int, required=True)  
    parser.add_argument("--frequency", type=float, required=True)  
    args = parser.parse_args()

    results = calculate_audio_metrics(
            file_path=args.input_file,
            sampling_rate=args.sampling_rate,
            f0=args.frequency)

    for key, value in results.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()
