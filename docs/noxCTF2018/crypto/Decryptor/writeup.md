# Decrypto

nc连接后是个RSA解密程序，发送c的16进制会返回解密后的m，但限制不能解密题目给的c。
可以把c分解为c1*c2。
因为 m=c^d mod n
    m=(c1*c2)^d mod n
    
设   m1=c1^d mod n, m2=c2^d mod n
则   m=(m1*m2) mod n

所以只要将c1,c2发送给服务端解密，得到m1和m2即可得到明文。

因数分解网站：[http://factordb.com/index.php](http://factordb.com/index.php)