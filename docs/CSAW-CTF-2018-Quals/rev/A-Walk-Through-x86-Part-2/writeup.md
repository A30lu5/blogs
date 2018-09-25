在radare中打开二进制文件

```c++
[0x00000000]> e asm.arch = x86
[0x00000000]> e asm.bits = 16
[0000:0000]> s 0x6000
[0000:6000]> pd 61
            0000:6000      f4             hlt
            0000:6001      e492           in al, 0x92
            0000:6003      0c02           or al, 2
            0000:6005      e692           out 0x92, al
            0000:6007      31c0           xor ax, ax
            0000:6009      8ed0           mov ss, ax
            0000:600b      bc0160         mov sp, 0x6001
            0000:600e      8ed8           mov ds, ax
            0000:6010      8ec0           mov es, ax
            0000:6012      8ee0           mov fs, ax
            0000:6014      8ee8           mov gs, ax
            0000:6016      fc             cld
            0000:6017      66bf00000000   mov edi, 0
        ┌─< 0000:601d      eb07           jmp 0x6026
        │   0000:601f      90             nop
        │   0000:6020      0000           add byte [bx + si], al
        │   0000:6022      0000           add byte [bx + si], al
        │   0000:6024      0000           add byte [bx + si], al
        └─> 0000:6026      57             push di
            0000:6027      66b900100000   mov ecx, 0x1000
            0000:602d      6631c0         xor eax, eax
            0000:6030      fc             cld
            0000:6031      f366ab         rep stosd dword es:[di], eax
            0000:6034      5f             pop di
            0000:6035      26668d850010   lea eax, dword es:[di + 0x1000]
            0000:603b      6683c803       or eax, 3
            0000:603f      26668905       mov dword es:[di], eax
            0000:6043      26668d850020   lea eax, dword es:[di + 0x2000]
            0000:6049      6683c803       or eax, 3
            0000:604d      266689850010   mov dword es:[di + 0x1000], eax ; [0x1000:4]=-1
            0000:6053      26668d850030   lea eax, dword es:[di + 0x3000]
            0000:6059      6683c803       or eax, 3
            0000:605d      266689850020   mov dword es:[di + 0x2000], eax ; [0x2000:4]=-1
            0000:6063      57             push di
            0000:6064      8dbd0030       lea di, word [di + 0x3000]
            0000:6068      66b803000000   mov eax, 3
        ┌─> 0000:606e      26668905       mov dword es:[di], eax
        ╎   0000:6072      660500100000   add eax, 0x1000
        ╎   0000:6078      83c708         add di, 8
        ╎   0000:607b      663d00002000   cmp eax, 0x200000
        └─< 0000:6081      72eb           jb 0x606e
            0000:6083      5f             pop di
            0000:6084      b0ff           mov al, 0xff                 ; 255
            0000:6086      e6a1           out 0xa1, al
            0000:6088      e621           out 0x21, al                 ; '!'
            0000:608a      90             nop
            0000:608b      90             nop
            0000:608c      0f011e2060     lidt [0x6020]
            0000:6091      66b8a0000000   mov eax, 0xa0                ; 160
            0000:6097      0f22e0         mov cr4, eax
            0000:609a      6689fa         mov edx, edi
            0000:609d      0f22da         mov cr3, edx
            0000:60a0      66b9800000c0   mov ecx, 0xc0000080
            0000:60a6      0f32           rdmsr
            0000:60a8      660d00010000   or eax, 0x100
            0000:60ae      0f30           wrmsr
            0000:60b0      0f20c3         mov ebx, cr0
            0000:60b3      6681cb010000.  or ebx, 0x80000001
            0000:60ba      0f22c3         mov cr0, ebx
            0000:60bd      0f0116e260     lgdt [0x60e2]
        ┌─< 0000:60c2      ea58610800     ljmp 8:0x6158
```

将hlt改为nop跳过。到0x6158

```c++
[0000:6000]> s 0x6158
[0000:6158]> e asm.bits = 64
[0x00006158]> pd 37
            0x00006158      66b81000       mov ax, 0x10                ; 16
            0x0000615c      8ed8           mov ds, eax
            0x0000615e      8ec0           mov es, eax
            0x00006160      8ee0           mov fs, eax
            0x00006162      8ee8           mov gs, eax
            0x00006164      8ed0           mov ss, eax
            0x00006166      bf00800b00     mov edi, 0xb8000
            0x0000616b      b9f4010000     mov ecx, 0x1f4              ; 500
            0x00006170      48b8201f201f.  movabs rax, 0x1f201f201f201f20
            0x0000617a      f348ab         rep stosq qword [rdi], rax
            0x0000617d      bf00800b00     mov edi, 0xb8000
            0x00006182      4831c0         xor rax, rax
            0x00006185      4831db         xor rbx, rbx
            0x00006188      4831c9         xor rcx, rcx
            0x0000618b      4831d2         xor rdx, rdx
            0x0000618e      b245           mov dl, 0x45                ; 'E' ; 69
            0x00006190      80ca6c         or dl, 0x6c                 ; 'l'
            0x00006193      b679           mov dh, 0x79                ; 'y' ; 121
            0x00006195      80ce6b         or dh, 0x6b                 ; 'k'
            0x00006198      20f2           and dl, dh
            0x0000619a      b600           mov dh, 0
            0x0000619c      48bee8600000.  movabs rsi, 0x60e8
        ┌─> 0x000061a6      48833c0600     cmp qword [rsi + rax], 0
       ┌──< 0x000061ab      7427           je 0x61d4
       │╎   0x000061ad      b904000000     mov ecx, 4
      ┌───> 0x000061b2      8a1c06         mov bl, byte [rsi + rax]
      ╎│╎   0x000061b5      30d3           xor bl, dl
      ╎│╎   0x000061b7      d0eb           shr bl, 1
      ╎│╎   0x000061b9      881c06         mov byte [rsi + rax], bl
      ╎│╎   0x000061bc      4883c002       add rax, 2
      └───< 0x000061c0      e2f0           loop 0x61b2
       │╎   0x000061c2      4883e808       sub rax, 8
       │╎   0x000061c6      488b0c06       mov rcx, qword [rsi + rax]
       │╎   0x000061ca      48890c07       mov qword [rdi + rax], rcx
       │╎   0x000061ce      4883c008       add rax, 8
       │└─< 0x000061d2      ebd2           jmp 0x61a6
       └──> 0x000061d4      ebd2           invalid
```

在栈上解密buf并且打印，解密算法如下
```python
import binascii

enc = binascii.unhexlify("a5b1aba79f09b5a3d78fb3010b0bd7fdf3c9d7a5b78dd7991905d7b7b50fd7b3018f8f0b85a3d70ba3ab89d701d7db09c393")
print("".join(chr((b ^ 0x69) >> 1) for b in enc))
```
