程序中使用了stl，存在4段check

第一段是一个aes，解密如下：

```c++
BYTE key[] = {
		0x2F,0xDF,0x09,0x58,0x4E,0xAC,0x6B,0x77,0xF4,0xDB,0x7F,0x7B,0xF7,0x99,0x9C,0x20,0xFF,0x80,0xCF,0x0C,0x7C,0x2A,0x29,0xCC,0xD6,0xC7,0x0C,0xBD,0x13,0xD1,0x40,0xB0
	};
	aes_context ctx;
	unsigned char iv[ 16*10 ];
	memset( &iv, 0, sizeof( iv ));
	BYTE szEnStr[] ={ 0xFF,0x80,0xCF,0x0C,0x7C,0x2A,0x29,0xCC,0xD6,0xC7,0x0C,0xBD,0x13,0xD1,0x40,0xB0};
	
	//解密	
	char szdeStr[1024] = {0};
	memset( &iv, 0, sizeof( iv ) );
	aes_setkey_dec( &ctx, (const unsigned char *)key, 128 );
	int nLen = 32;
	aes_crypt_cbc( &ctx, AES_DECRYPT,nLen , iv,(const unsigned char *)&szEnStr, (unsigned char *)&szdeStr );
	printf("解密后数据：%s\n",szdeStr);
```

第二段从map中取了对应的字节然后做了变序运算，然后跟固定buf比较,map初始化数据在0564838处。

```python
 def mkmap():
        r = {}
        s = [0x42, 0xf8, 0x64, 0xd0, 0x68, 0xe3, 0x6c, 0xb6, 0x6e, 0x85, 0x31, 0xf5, 0x30, 0xb7, 0x33, 0xc8, 0x54, 0x88, 0x5f, 0xe8]
        for i in range(0, len(s) / 2):

            r[s[i*2 + 1]] = s[i*2]

        return r

    r1 = bytearray([0xe8, 0xb6, 0xf5, 0xc8, 0x85, 0xe3, 0xc8, 0xf8, 
                    0xe8, 0x85, 0x88, 0xb7, 0xd0])
    
    r1 = xchg(r1, 4, 10)
    r1 = r1[-3:] + r1[:-3]
    r1 = xchg(r1, 11, 10)
    r1 = xchg(r1, 0, 5)
    r1 = xchg(r1, 4, 1)
    r1 = r1[7:] + r1[:7]
    r1 = xchg(r1, 5, 7)
    r1 = xchg(r1, 2, 0xc)

    mp = mkmap()
    for i in range(0, len(r1)):
        if r1[i]:
            r1[i] = mp[r1[i]]

    r.sendlineafter("Earth Kingdom:", str(r1)) # Th3_Bl1nd_0n3
```

第三段是一个表达式求解，可存在多个解

```c++
bool __fastcall Check3333333333333333333333333333333333333333333333333333333(char *szIn)
{
  return (((14 * (((std::__cxx11::stoll(szIn, '\0', 16LL) | 0x40) - 0x5336654 + 0x1E240) | 0x10000) >> 1) - 0x3B93AE7C) & 0xFFFFFFFFFFFF7FFFLL ^ 0x6E988) == 0x1CDEDC990D1LL;
}
```

```python
from z3 import *
import os
solver = Solver()
source = BitVec('source', 64)
x = Int('x')

solver.add((((14 * (((source | 0x40) - 87254612 + 123456) | 0x10000) >> 1) - 999534204) & 0xFFFFFFFFFFFF7FFF ^ 0x6E988) == 1983969333457)

while 1:
    if solver.check()!=sat:
        break
    result = solver.model()[source].as_long()
    print hex(result)
    solver.add(source!=result)
    
```

得到的解其中一个可以通过第三段验证。

第四段是将输入做哈希，分为6段再计算哈希，分别比较。

```
3c9314956b8ecf32f6745a3d7b98338f6b48b584c5e1250feb3e79bfb2a6d5c7 a76857 
f288534efaf4c06262adea0158526b3bd2985b7a2112a30dadaf9eaa90ad9701 f5cbff
7e0f334f9a5012575aeceec44686b102cf8849ab32cd797f157f09961041231a 7d4a83
f84a58f150a0d9cb21c67ec27970f9cad863c76be773c8417650d63c13352e66 60602b
27fe87f345ea08a26e8f732f5120e2ef419b9a03a6ef14e8f18a3b83bd41a81c da247a
8bd574fdb05c2dc5017188a2f4c32d5b81963e0a33eccba92404e968c665006d fd
```

在计算一次：

`a76857f5cbff7d4a8360602bda247afd MD5 : B41dy`

分别输入得到正确的flag：`noxCTF{Fu11_M00n-Th3_Bl1nd_0n3-420B1B2E57-B41dy}`

















































