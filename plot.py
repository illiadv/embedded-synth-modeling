import matplotlib.pyplot as plt
import numpy as np
import os
import argparse

def plot_spectrum(file_path: str, sample_rate: int = 8000):
    
    data = np.fromfile(file_path, dtype=np.int16)
    n = len(data)

    if n == 0:
        raise ValueError("File is empty.")

    # Apply a window function to reduce spectral leakage
    window = np.hanning(n)
    windowed_data = data * window

    # Compute one-sided real FFT
    # The output spans frequencies from 0 Hz up to the Nyquist limit (sample_rate / 2 = 4000 Hz)
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate)
    fft_vals = np.fft.rfft(windowed_data)

    # Compute magnitude, normalize by window coherent gain, and scale for single-sided spectrum
    magnitude = np.abs(fft_vals) / np.sum(window)
    magnitude[1:-1] *= 2

    # Convert to decibels relative to full scale (dBFS for 16-bit max value 32767)
    ref = 32767.0
    magnitude_db = 20 * np.log10(np.maximum(magnitude, 1e-12) / ref)

    # Plot
    plt.figure(figsize=(10, 4))
    plt.plot(freqs, magnitude_db)

    plt.title(f"Frequency Spectrum ({sample_rate} Hz Mono PCM ({file_path})")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dBFS)")
    plt.xlim(0, sample_rate / 2)
    plt.ylim(-120, 0)
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)  
    parser.add_argument("--sampling-rate", type=int, required=True)  
    args = parser.parse_args()

    plot_spectrum(args.input_file, args.sampling_rate)

if __name__ == "__main__":
    main()
