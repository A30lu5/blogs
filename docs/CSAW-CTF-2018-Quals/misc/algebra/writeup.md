
# algebra

使用z3求解或者sympy求解
exp1.py
```py
from z3 import *
from pwn import *
context.log_level = "DEBUG"

#p = process("./algebra.py")

p = remote("misc.chal.csaw.io", 9002)
count = 0
p.recvuntil('**********************************************************************************\n')
while(1):
    equ = p.recvline()
    p.recvuntil("?:") #eat interstitial

    e = equ.split(" = ")

    s = Solver()
    X = Real("X")
    s.add(eval(e[0])== int(e[1].strip()))
    print count
    print s.check()
    print(s.model())
    ans = s.model()[X]

    anstr = ans.as_string()
    if "/" in anstr:
        anstr = str(eval(anstr + ".0"))

    p.sendline(anstr)
    p.recvline()
    count += 1
```

exp2.py
```py
from __future__ import division
from sympy import *
from pwn import *
X=Symbol('X')
r=remote('misc.chal.csaw.io',9002)
print r.recvuntil('**********************************************************************************\n')
while 1:
    a=r.recvline()
    print a,
    ans=str(eval(str(solve(a.replace('=','-')[:-1], X)[0])))
    print ans,
    r.sendline(ans)
    feedback=r.recvline()
    print feedback
```