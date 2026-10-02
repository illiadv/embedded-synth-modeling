from pyrenode3.wrappers import Emulation, Monitor
import os

cwd = os.getcwd()
output_dir = os.path.join(cwd, "output")
if not os.path.isdir(output_dir):
    print(f"{output_dir} is not a directory! Aborting.")
    exit(1)

output_filename = os.path.join(output_dir, "dump.bin")

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
    filename = '{output_filename}'

    data = sysbus.ReadBytes(address, width)
    with open(filename, 'ab') as f: f.write(bytes(data))
    cpu.InfoLog('Hook finished')
    if value == 4:
	cpu.InfoLog('Finished writing')
	cpu.Pause()
"""

hook_address = stm32.sysbus.GetSymbolAddress("g_buffer_fill_count")
# stm32.sysbus.AddWatchpointHook(
