import subprocess
import shlex
from pyrenode3.wrappers import Analyzer, Emulation, Monitor, TerminalTester

e = Emulation()
m = Monitor()

stm32 = e.add_mach()
assert stm32 is not None
stm32.load_repl("platforms/cpus/stm32f4.repl")
stm32.load_elf("build/Debug/f401.elf")
stm32.sysbus.timer1.Frequency = 8000000

stm32.StartGdbServer(3333)

cmd_gdb = """arm-none-eabi-gdb -batch
    -ex "source gdb_count_inst.py"
    -ex "target remote :3333"
    -ex "break GetSample_wt_trunc"
    -ex "continue"
    -ex "count_inst"
    ./build/Debug/f401.elf
"""

args_gdb = shlex.split(cmd_gdb)

proc_gdb = subprocess.Popen(args_gdb, stdout=subprocess.PIPE, text=True)
proc_grep = subprocess.Popen(["grep", "Total"], stdin=proc_gdb.stdout, stdout=subprocess.PIPE, text=True)

assert proc_gdb.stdout is not None

proc_gdb.stdout.close()
output, _ = proc_grep.communicate();

print(f"Output: {output}")
