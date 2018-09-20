# Read Between The Lines

file发现是gzip compressed data，解了之后打开首先看到一段jsfuck

解开后发现只是一个弹窗的代码

![](./images/1.png)

这时发现jsfuck下还有一大堆的空白，感觉很奇怪，于是全选了下

![](./images/2.png)

这看起来很像whitespace，找了个解释器跑一下就出flag了

![](./images/3.png)