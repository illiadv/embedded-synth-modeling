import os
import time
import argparse

from pyrenode3.wrappers import Emulation, Monitor, TerminalTester
from Antmicro.Renode.Peripherals.Bus import Access, SysbusAccessWidth

from setup import setup_stm32

buffer_size = 512
bytes_per_sample = 2

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sampling-rate", type=int, required=True)  
    args = parser.parse_args()
    return args


def touch_output_file(output_dir: str) -> str:
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass
    except Exception:
        print(f"Could not create directory {output_dir}. Aborting.")
        exit(1)

    output_path = os.path.join(output_dir, "dump.bin")

    try:
        open(output_path, "w")
    except Exception as e:
        print(f"Could not create empty output file: {e}")
        exit(1)
    else:
        print(f"Created empty file {output_path}")

    return output_path

def main():

    args = parse_args()
    assert args is not None

    cwd = os.getcwd()
    output_dir = os.path.join(cwd, "output")
    output_path = touch_output_file(output_dir)

    e = Emulation()
    m = Monitor()

    m.execute(f"logFile @{os.path.join(output_dir, "renode.log")}")

    stm32 = setup_stm32(e)

    t = TerminalTester(stm32.sysbus.usart2, 0.1)
    e.StartAll()

    result = t.WaitFor([f"Rate: {args.sampling_rate}"], includeUnfinishedLine=True)
    if (result == None):
        print("Sampling rate test failed:")
        print(t.GetReport())
        exit(1)
    else:
        print("Sampling rate test passed")

    buffer_full_hook = f"""
if value != 0:
    sysbus = cpu.GetMachine()['sysbus']

    address = sysbus.GetSymbolAddress('g_buffer')

    sampling_rate = {args.sampling_rate}
    buffer_size = {buffer_size}
    filename = '{output_path}'
    samples_written = value

    width = buffer_size * {bytes_per_sample}

    if samples_written > sampling_rate:
        width = (buffer_size - (samples_written - sampling_rate))
        width *= {bytes_per_sample}

    data = sysbus.ReadBytes(address, width)
    with open(filename, 'ab') as f: f.write(bytes(data))
    print '%d bytes written' % width

    if samples_written > sampling_rate:
        print 'Finished writing'
        cpu.Pause()
"""

    try:
        hook_trigger_address = stm32.sysbus.GetSymbolAddress("g_buffer_samples_written")
        stm32.sysbus.AddWatchpointHook(hook_trigger_address, SysbusAccessWidth.DoubleWord, Access.Write, buffer_full_hook)
    except Exception as e:
        print(f"Exception: {e}")
        exit(1)


    time.sleep(5);
    print("Exiting")

if __name__ == "__main__":
    main()
