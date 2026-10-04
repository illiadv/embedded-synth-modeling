from pyrenode3.wrappers import Emulation, Monitor
from Antmicro.Renode.Peripherals.Bus import Access, SysbusAccessWidth
import os
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--sampling-rate", type=int, required=True)  
args = parser.parse_args()

buffer_size = 512

cwd = os.getcwd()
output_dir = os.path.join(cwd, "output")
if not os.path.isdir(output_dir):
    print(f"{output_dir} is not a directory! Aborting.")
    exit(1)

output_path = os.path.join(output_dir, "dump.bin")

try:
    open(output_path, "w")
except Exception as e:
    print(f"Could not create empty output file: {e}")
    exit(1)
else:
    print(f"Created empty file {output_path}")

e = Emulation()
m = Monitor()

stm32 = e.add_mach()
assert stm32 is not None
stm32.load_repl("platforms/cpus/stm32f4.repl")
stm32.load_elf("build/Debug/f401.elf")
stm32.sysbus.timer1.Frequency = 8000000



buffer_full_hook = f"""
if value != 0:
    sysbus = cpu.GetMachine()['sysbus']

    address = sysbus.GetSymbolAddress('g_buffer')

    sampling_rate = {args.sampling_rate}
    buffer_size = {buffer_size}
    filename = '{output_path}'
    bytes_written = value

    width = buffer_size

    if bytes_written > sampling_rate:
        width = buffer_size - (bytes_written - sampling_rate)

    data = sysbus.ReadBytes(address, width)
    with open(filename, 'ab') as f: f.write(bytes(data))
    print '%d bytes written' % width

    if bytes_written > sampling_rate:
        print 'Finished writing'
        cpu.Pause()
"""

try:
    hook_trigger_address = stm32.sysbus.GetSymbolAddress("g_buffer_bytes_written")
    stm32.sysbus.AddWatchpointHook(hook_trigger_address, SysbusAccessWidth.DoubleWord, Access.Write, buffer_full_hook)
except Exception as e:
    print(f"Exception: {e}")
    exit(1)

e.StartAll()

time.sleep(5);
print("Exiting")
