## Att3nti0n

直接Ida打开可以直接定位到验证函数

```c++
int __cdecl main(int argc, const char **argv, const char **envp)
{
  int result; // eax

  __main();
  if ( argc == 2 )
  {
    if ( (unsigned __int8)CheckKey(argv[1]) == 1 )
      fwrite("Correct! :)\n", 1u, 0xCu, (FILE *)__iob[0]._ptr);
    else
      fwrite("Not correct password! :(\n", 1u, 0x19u, &__iob[2]);
    getchar();
    result = 0;
  }
  else
  {
    fwrite("Usage: F_ckIt.exe <Decrypted key>\n", 1u, 0x22u, &__iob[2]);
    result = 1;
  }
  return result;
}
```

对CheckKey函数进行逆向，该函数的功能是对输入的key与4字节数组循环异或。然后跟一个固定的buf去对比，解密这个buf如下：

```c++
BYTE g_array1[] = {0x13,0x37,0x73,0x31};
BYTE g_array2[] =
{
	0x7d, 0x58, 0x0b, 0x65, 0x55, 0x4c, 0x35, 0x50, 0x78, 0x52, 0x53, 0x41, 0x72, 0x44, 0x00, 0x46,
	0x7c, 0x45, 0x17, 0x1f, 0x3d, 0x17, 0x35, 0x58, 0x7d, 0x53, 0x53, 0x42, 0x7c, 0x5a, 0x16, 0x45,
	0x7b, 0x5e, 0x1d, 0x56, 0x33, 0x52, 0x1f, 0x42, 0x76, 0x17, 0x1a, 0x5f, 0x60, 0x5e, 0x17, 0x54,
	0x33, 0x43, 0x1b, 0x54, 0x33, 0x55, 0x1a, 0x5f, 0x72, 0x45, 0x0a, 0x4c
	

};
for (int i=63;i>=0;)
	{
		BYTE v3 =  g_array1[i % 4];
		int v4 = i--;
		char c =v3^g_array2[v4];
		szFlag[i+1] = c;
		printf("%c",c);
	}
```

但是得到的结果为

`noxTF{Fake password.. Find something else inside the binary}`

并不是改程序正确的key。

仔细查看程序，0x00401560存在一个未使用的函数。分析该函数，是先初始化一块局部变量buf，然后判断这块buf的开头4字节是否为0x55 ,0x89,0xe5,0x60，然后对这块buf进行了一些修改操作，然后申请一块可执行内存拷贝过去运行，那么我们猜测这块内存是一段可执行代码，使用上面的解密函数，对这块buf进行解密，得到的结果如下:

```c++
00030000    55              push ebp
00030001    89E5            mov ebp,esp
00030003    60              pushad
00030004    31C0            xor eax,eax
00030006    BE AEF92800     mov esi,0x28F9AE                         ; ASCII "yxoCQl_&ss$yHQBYt &'y"H#e$HT''&6j"
0003000B    BF AEF92800     mov edi,0x28F9AE                         ; ASCII "yxoCQl_&ss$yHQBYt &'y"H#e$HT''&6j"
00030010    AC              lods byte ptr ds:[esi]
00030011    84C0            test al,al
00030013    74 05           je short 0003001A
00030015    34 17           xor al,0x17
00030017    AA              stos byte ptr es:[edi]
00030018  ^ EB F6           jmp short 00030010
0003001A    61              popad
0003001B    89EC            mov esp,ebp
0003001D    5D              pop ebp
0003001E    C3              ret


```

最后call eax跳入执行，得到的结果就是正确的flag。

`noxTF{H1dd3n_FUNc710n5_4r3_C001!}`





