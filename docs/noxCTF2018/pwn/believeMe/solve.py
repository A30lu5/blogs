# return (((14 * (((std: : __cxx11: : stoll(szIn, '\0', 16LL) | 0x40) - 0x5336654 + 0x1E240) | 0x10000) >> 1) - 0x3B93AE7C) & 0xFFFFFFFFFFFF7FFFLL ^ 0x6E988) == 0x1CDEDC990D1LL

a = 0x1CDEDC990D1 ^ 0x6E988
b = a | 0x0000
c = b + 0x3B93AE7C
d = c <<1
e = d/14
print "The c: ", c
for i in range(0, 5):
    # if (d+i) %14 ==0:
        print i, d+i, hex((d+i)/14), ((d+i)/14)*14>>1
# print hex(c)
# print hex(d)
# print hex(e)
