from pyrenode3.wrappers import Analyzer, Emulation, Monitor, TerminalTester

e = Emulation()
m = Monitor()

stm32 = e.add_mach()
assert stm32 is not None
stm32.load_repl("platforms/cpus/stm32f4.repl")
stm32.load_elf("build/Debug/f401.elf")
stm32.sysbus.timer1.Frequency = 8000000

buffer_full_hook = """
if value != 0:
    sysbus = cpu.GetMachine()['sysbus']

    address = sysbus.GetSymbolAddress('g_buffer')
    width = 4000
    filename = '/home/user/src/my/renode/f401/output/dump.bin'

    data = sysbus.ReadBytes(address, width)
    with open(filename, 'ab') as f: f.write(bytes(data))
    cpu.InfoLog('Hook finished')
    if value == 4:
	cpu.InfoLog('Finished writing')
	cpu.Pause()
"""

hook_address = stm32.sysbus.GetSymbolAddress("g_buffer_fill_count")
# stm32.sysbus.AddWatchpointHook(
