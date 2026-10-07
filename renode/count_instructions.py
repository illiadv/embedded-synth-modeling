import sys
import subprocess
import shlex
import argparse
from pyrenode3.wrappers import Emulation, Monitor

parser = argparse.ArgumentParser()
parser.add_argument("--impl-name", type=str, required=True)  
args = parser.parse_args()
impl_name = args.impl_name

parser = argparse.ArgumentParser

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

cmd_gdb = f"""gdb-multiarch -batch
    -ex "source renode/gdb_count_inst.py"
    -ex "target remote :3333"
    -ex "break GetSample_{impl_name}"
    -ex "continue"
    -ex "count_inst"
    ./build/Debug/f401.elf
"""

args_gdb = shlex.split(cmd_gdb)

# TODO: must fail if gdb process fails
proc_gdb = subprocess.Popen(args_gdb, stdout=subprocess.PIPE, text=True)
proc_grep = subprocess.Popen(["grep", "Instructions executed"], stdin=proc_gdb.stdout, stdout=subprocess.PIPE, text=True)

assert proc_gdb.stdout is not None

proc_gdb.stdout.close()
output, _ = proc_grep.communicate();

print(f"{output}")
