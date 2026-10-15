from pyrenode3.wrappers import Emulation, Machine

def setup_stm32(e: Emulation) -> Machine:
    stm32 = e.add_mach()
    assert stm32 is not None
    stm32.load_repl("platforms/cpus/stm32f4.repl")
    stm32.load_elf("build/Debug/f401.elf")
    stm32.sysbus.timer1.Frequency = 8000000
    return stm32
