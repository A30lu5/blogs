##  Guess the string

ida打开看下，满足程序的所有条件即可得到flag。

```c++
_BOOL8 __fastcall O0000OOO00(__int64 a1, int a2)
{
  char v2; // dl
  char v3; // dl

  return (unsigned int)O0OO0O0O0O((const char *)a1)
      && (unsigned int)OOO00O0O00(a1)
      && (unsigned int)O0OO0O0O00(a1)
      && (unsigned int)O000O00O00(a1)
      && (unsigned int)OO000OO000(a1)
      && (unsigned int)O0OO0O00OO(a1)
      && (unsigned int)OOO00O00O0(a1)
      && (unsigned int)OO00O0O000(a1)
      && (unsigned int)O00OOOO000(a1, a2, v2)
      && (unsigned int)OOOOO00O00(a1)
      && (unsigned int)O00OO0O0OO(a1, a2, v3);
}
```

罗列一下：

* 长度11
* ascii>32
* szIn[0]！=B   szIn[0]*szIn[1] = 0xd96
* ((szIn[1] ^ szIn[0]) ^ szIn[2]) = 0x31
* (char)szIn[3] > (char)szIn[2]   szIn[2] * szIn[2] == szIn[3] * szIn[3]

后面用到一个函数

```c++
BOOL CheckNo0(BYTE bIn)
{
	signed int i; // [rsp+Ch] [rbp-8h]
	unsigned int v3; // [rsp+10h] [rbp-4h]

	v3 = 1;
	if ( bIn > 1u )
	{
		if ( bIn > 2u )
		{
			for ( i = 2; v3 && i < bIn; ++i )
			{
				if ( !(bIn % i) )
					v3 = 0;
			}
		}
	}
	else
	{
		v3 = 0;
	}
	return v3;
}
```

直接抄下来用了，其实就是判断是否为质数

* szIn[4]  szIn[5]是质数并且  szIn[4] ^ szIn[5]) == 126
* CheckNo0((char)szIn[6] / 2)            (char)szIn[6] == 2 * ((char)szIn[5] - 42)
* szIn[7] > 47  szIn[7] <= 57  4 * (char)((char)szIn[7] >> 2) == (char)szIn[7]
* szIn[8] == (a1 ^ szIn[7])
* 2 * szIn[8] == szIn[9]

```python
#!/usr/bin/env python3

primes = []

for i in range(2, 256):
    for j in range(2, i):
        if i % j == 0:
            break
    else:
        primes.append(i)

s = [0] * 11

s[0] = 47
s[1] = 74

assert(s[0] * s[1] == 3478)

s[2] = s[0] ^ s[1] ^ 49

for i in range(s[2] + 1, 256):
    if i * i % 256 == s[2] * s[2] % 256:
        s[3] = i
        break

def get456():
    for i in primes:
        for j in primes:
            if i > 32 and j > 32 and (i ^ j) % 256 == 126:
                if j - 42 in primes and 2 * j < 256:
                    return (i, j, 2 * (j - 42))

s[4], s[5], s[6] = get456()

for i in range(48, 58):
    if 4 * (i >> 2) == i:
        s[7] = i
        break

s[8] = 0x12 ^ s[7]

s[9] = 2 * s[8]

s[10] = 0x7a

for c in s:
    assert(c > 32)

print(''.join(map(chr, s)))
```



