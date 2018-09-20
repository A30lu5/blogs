# Python for fun

浏览整站，在 `match_signature_to_body` 这个功能有用户交互，测试后发现这里可以任意代码执行，而且没有过滤，所以直接就可以import os来进行系统命令执行

![](./images/1.png)

然后 `cat FLAG` 得到flag

![](./images/2.png)