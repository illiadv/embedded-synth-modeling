import sys
import subprocess
import shlex
import argparse

from pyrenode3.wrappers import Emulation

from setup import setup_stm32

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--impl-name", type=str, required=True)  
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    assert args is not None

    e = Emulation()
    stm32 = setup_stm32(e)

    try:
        stm32.sysbus.GetSymbolAddress(f"GetSample_{args.impl_name}")
    except Exception as e:
        print(f"No symbol for selected implementation {args.impl_name} found")
        exit(1)

    stm32.StartGdbServer(3333)

    cmd_gdb = f"""gdb-multiarch -batch
        -ex "source renode/gdb_count_inst.py"
        -ex "target remote :3333"
        -ex "break GetSample_{args.impl_name}"
        -ex "continue"
        -ex "count_inst"
        ./build/Debug/f401.elf
    """
    args_gdb = shlex.split(cmd_gdb)

    # TODO: must fail if gdb process fails
    proc_gdb = subprocess.Popen(args_gdb, stdout=subprocess.PIPE, text=True)
    proc_grep = subprocess.Popen(["grep", "Instructions:"], stdin=proc_gdb.stdout, stdout=subprocess.PIPE, text=True)

    assert proc_gdb.stdout is not None

    proc_gdb.stdout.close()
    output, _ = proc_grep.communicate();

    print(f"{output}")

if __name__ == "__main__":
    main()
