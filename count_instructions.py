import sys
import subprocess
import shlex
from pyrenode3.wrappers import Emulation, Monitor

try:
    impl_name = sys.argv[1]
except IndexError:
    print("No implementation name provided! Aborting.")
    exit(1)

e = Emulation()
m = Monitor()

stm32 = e.add_mach()
assert stm32 is not None
stm32.load_repl("platforms/cpus/stm32f4.repl")
stm32.load_elf("build/Debug/f401.elf")
stm32.sysbus.timer1.Frequency = 8000000

try:
    stm32.sysbus.GetSymbolAddress(f"GetSample_{impl_name}")
except Exception as e:
    print(f"No symbol for selected implementation {impl_name} found")
    exit(1)

stm32.StartGdbServer(3333)

cmd_gdb = f"""arm-none-eabi-gdb -batch
    -ex "source gdb_count_inst.py"
    -ex "target remote :3333"
    -ex "break GetSample_{impl_name}"
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
