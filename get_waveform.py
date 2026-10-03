from pyrenode3.wrappers import Emulation, Monitor
from Antmicro.Renode.Peripherals.Bus import Access, SysbusAccessWidth
import os
import time

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
    width = 4000
    filename = '{output_path}'

    data = sysbus.ReadBytes(address, width)
    with open(filename, 'ab') as f: f.write(bytes(data))
    print 'Hook finished'
    if value == 4:
	print 'Finished writing'
	cpu.Pause()
"""

hook_trigger_address = stm32.sysbus.GetSymbolAddress("g_buffer_fill_count")
stm32.sysbus.AddWatchpointHook(hook_trigger_address, SysbusAccessWidth.DoubleWord, Access.Write, buffer_full_hook)

e.StartAll()

time.sleep(5);
print("Exiting")
