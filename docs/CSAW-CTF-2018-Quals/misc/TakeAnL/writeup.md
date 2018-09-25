# TakeAnL

算法中的棋盘覆盖问题，可以使用分治思想求解。
参考链接:https://blog.csdn.net/yinaoxiong/article/details/53761608

exp.py
```py
from __future__ import print_function
from pwn import *
def chess(tr, tc, pr, pc, size):
    global mark
    global table
    mark += 1
    count = mark
    if size == 1:
        return
    half = size // 2
    if pr < tr + half and pc < tc + half:
        chess(tr, tc, pr, pc, half)
    else:
        table[tr + half - 1][tc + half - 1] = count
        chess(tr, tc, tr + half - 1, tc + half - 1, half)
    if pr < tr + half and pc >= tc + half:
        chess(tr, tc + half, pr, pc, half)
    else:
        table[tr + half - 1][tc + half] = count
        chess(tr, tc + half, tr + half - 1, tc + half, half)
    if pr >= tr + half and pc < tc + half:
        chess(tr + half, tc, pr, pc, half)
    else:
        table[tr + half][tc + half - 1] = count
        chess(tr + half, tc, tr + half, tc + half - 1, half)
    if pr >= tr + half and pc >= tc + half:
        chess(tr + half, tc + half, pr, pc, half)
    else:
        table[tr + half][tc + half] = count
        chess(tr + half, tc + half, tr + half, tc + half, half)


def show(table):
    n = len(table)
    for i in range(n):
        for j in range(n):
            print(table[i][j], end='	')
        print('')



r=remote('misc.chal.csaw.io',9000)
print(r.recvuntil('marked block:'))
d=r.recv()
print(d)
a=int(d[2:4])
b=int(d[5:8].rstrip(')'))

mark = 0
n = 64
table = [[-1 for x in range(n)] for y in range(n)]
chess(0, 0, a, b, n)
dict=[]
for i in table:
    for j in i:
        if j not in dict and j !=-1:
            dict.append(j)
index=[]
for i in range(len(dict)):
    index.append([])
p=0
for d in dict:
    for i in range(n):
        for j in range(n):
            if table[i][j]==d:
                index[p].append((i,j))
            else:
                pass
    p=p+1
# show(table)
# print(index)

ans=''
for i in range(len(index)):
    ans+=str(index[i][0])+','+str(index[i][1])+','+str(index[i][2])+'\n'
print(ans)
r.sendline(ans)
print(r.recvline())
```

