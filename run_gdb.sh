#/bin/sh

renode gdb.resc &

arm-none-eabi-gdb -batch \
    -ex "source	count_instructions.py" \
    -ex "target remote :3333" \
    -ex "break GetSample_$1" \
    -ex "continue" \
    -ex "count_inst" \
    ./build/Debug/f401.elf

pkill -SIGTERM dotnet
