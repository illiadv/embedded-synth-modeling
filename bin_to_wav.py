import argparse
import sys
import wave

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Path to the input raw PCM binary file")
    parser.add_argument("output_file", help="Path to the output .wav file")
    parser.add_argument("sampling_rate", type=int, help="Sampling rate in Hz")
    args = parser.parse_args()

    if args.sampling_rate <= 0:
        parser.error("sampling_rate must be a positive integer.")

    return args

def pcm_to_wav(input_file, output_file, sampling_rate):
    bytes_per_sample = 2  # 16-bit PCM = 2 bytes

    try:
        with open(input_file, "rb") as pcm_in, wave.open(output_file, "wb") as wav_out:
            # Set WAV file parameters
            wav_out.setnchannels(1)
            wav_out.setsampwidth(bytes_per_sample)
            wav_out.setframerate(sampling_rate)

            # Read and write in 4KB chunks
            chunk_size = 4096
            while chunk := pcm_in.read(chunk_size):
                wav_out.writeframes(chunk)

        print(f"Successfully converted '{input_file}' to '{output_file}'.")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    args = parse_args()
    pcm_to_wav(args.input_file, args.output_file, args.sampling_rate)


if __name__ == "__main__":
    main()
