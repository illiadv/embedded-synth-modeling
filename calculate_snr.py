import numpy as np
import argparse

def calculate_snr(
    file_path: str = "waveform_dump.bin",
    sampling_rate: int = 8000,
    f0: float = 220.0,
) -> float:
    # 1. Load 16-bit signed PCM data
    data = np.fromfile(file_path, dtype=np.int16).astype(np.float64)
    n = len(data)
    if n == 0:
        raise ValueError("The provided file is empty.")

    # 2. Create time vector
    t = np.arange(n) / sampling_rate

    # 3. Build the design matrix for least-squares sine wave fitting
    # Model: A*sin(2*pi*f0*t) + B*cos(2*pi*f0*t) + C (DC offset)
    omega = 2 * np.pi * f0
    X = np.column_stack((np.sin(omega * t), np.cos(omega * t), np.ones(n)))

    # 4. Solve for coefficients [A, B, C]
    coeffs, _, _, _ = np.linalg.lstsq(X, data, rcond=None)

    # 5. Reconstruct the ideal AC signal (ignoring the DC offset)
    ideal_ac_signal = coeffs[0] * np.sin(omega * t) + coeffs[1] * np.cos(omega * t)
    
    # 6. Calculate the noise
    total_fit = ideal_ac_signal + coeffs[2]
    noise = data - total_fit

    # 7. Calculate power and SNR
    signal_power = np.mean(ideal_ac_signal**2)
    noise_power = np.mean(noise**2)

    if noise_power == 0:
        return float('inf')
        
    snr_db = 10 * np.log10(signal_power / noise_power)
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
