程序的区段名字被修改为upx，中间穿插了大量的花指令。首先程序自己注册了异常处理函数，异常处理函数中进行了flag的校验。
通过对程序的输入下硬件访问断电，定位到算法校验处

```
00528109   /75 0B           jnz short 1337.00528116
0052810B   |68 00805200     push 1337.00528000
00528110   |FF15 20506700   call dword ptr ds:[<&KERNEL32.LoadLibrar>; kernel32.LoadLibraryA
00528116   \FF75 0C         push dword ptr ss:[ebp+0xC]
00528119    FF75 08         push dword ptr ss:[ebp+0x8]
0052811C    E8 FFFEFFFF     call 1337.00528020                       ; 对输入进行计算
00528121    8BF0            mov esi,eax
00528123    8BFA            mov edi,edx
00528125    85C0            test eax,eax
00528127    75 07           jnz short 1337.00528130
00528129    A1 3C516700     mov eax,dword ptr ds:[<&USER32.SwitchDes>
0052812E    FFD0            call eax
00528130    8BD7            mov edx,edi
00528132    8BC6            mov eax,esi
00528134    5F              pop edi
00528135    5E              pop esi
00528136    5D              pop ebp
00528137    C2 0800         ret 0x8
```
0052811C处的call对输入进行计算，参数如下：

```
0015E8F4   33323130  |Arg1 = 33323130
0015E8F8   37363534  \Arg2 = 37363534
```
返回值在eax跟edx中。继续跟踪eax与edx寄存器的值，会找到对应比较的密文

```
0xbeb9e408e58575b0
0xb8f8437f04f80044
0xc227df7146b09474
```

分析00528020处的算法

转成python表示如下：
```python
   def mul(val):
      # val is a 8B input chunk
      res = (val >> 62) + pow(5, val, 2**64) - 1
      return res & 0xffffffffffffffff
```
解密脚本如下：
```python
import string
import itertools

magic1 = 0xbeb9e408e58575b0
magic2 = 0xb8f8437f04f80044
magic3 = 0xc227df7146b09474

test = "T3stT3St"
test_val = int(test[::-1].encode("hex"), 16)

def int_to_str(val):
    val = "{:016x}".format(val)
    return val.decode("hex")[::-1]

def mul(val):
    res = (val >> 62) + pow(5, val, 2 ** 64) - 1
    return res & 0xffffffffffffffff

def solve(num, lvl, magic, inputs):
    # Stop. If we consumed 8B we have a solution
    if lvl == 8:
        inputs.append(int_to_str(num)) 
        return

    # Prepare mask
    mask = 0xff
    for i in range(0, lvl):
        mask = (mask << 8) | 0xff 
    
    # Bruteforce
    for c in string.printable:
        test_num = ord(c) << ((lvl)*8) | num
        res = mul(test_num)
        # If input byte matches, go deeper
        if res & mask == magic & mask:
            solve(test_num, lvl+1, magic, inputs)


test_res = mul(test_val)
retrotest = []
solve(test_val & (1 << 62), 0, test_res, retrotest)
assert test == retrotest[0]

found1 = []
found2 = []
found3 = []

solve(0, 0, magic1, found1)
# solve(1 < 62, 0, magic1, found1)
solve(0, 0, magic2, found2)
# solve(1 < 62, 0, magic2, found2)
solve(0x0, 0, magic3, found3)
# solve(1 < 62, 0, magic3, found3)

for flag in itertools.product(found1, found2, found3):
    print "flag{%s}" % ("".join(flag))
```

最终得到flag

`flag{4.\/3ry.1337.|>45$vVp@9/}`



