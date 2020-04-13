PyJSCaller
===============
[![Build Status](https://img.shields.io/badge/build-passing-green.svg)](https://github.com/ZSAIm/PyJSCaller)
[![Build Status](https://img.shields.io/badge/pypi-v0.2.1-blue.svg)](https://pypi.org/project/PyJSCaller/)


Python 调用执行 JavaScript 代码。

PyJSCaller 是 Python 和 JavaScript 之间代理，是为了使 JavaScript 的代码调用更像是在使用 Python 一样。

一个简短的例子：
*****

> example.js
    
```javascript
 function add(a, b){
    return a + b;
 }
```

# 用法

### 调用方式一：

```python
>>> import jscaller
>>> jscaller.eval("'Hello World!'.toUpperCase()")
'HELLO WORLD!'
```

### 调用方式二：

```python
>>> ctx = jscaller.compile('example.js', timeout=3)
>>> ctx.call('add', 1, 1)
2
```

### 调用方式三：

```python
>>> with jscaller.session('example.js') as sess:
...     add, math = sess.get('add', 'Math')
...     res1 = add(2, 3)
...     res2 = math.PI + math.E
...     sess.call(res1, res2)
...
>>> res1.get_value()
5
>>> res2.get_value()
5.859874482048838
```

### 切换JS运行时引擎：

```python
>>> from jscaller.engine import PhantomJS
>>> PhantomJS.test()
2.1.1
>>> PhantomJS.config(timeout=10)
>>> jscaller.make(PhantomJS)
>>> jscaller.eval('1+1')
2

```

### 


# 支持的JS引擎

* [NodeJS](https://nodejs.org/) - 默认
* [PhantomJS](https://phantomjs.org/)


# 安装

    $ pip install PyJSCaller


# 许可证
MIT license

# 更新日志

### 0.2.0
- 简化使用流程。
- 支持 Python 3.x.x。
- 支持 Python 2.7.x。

### 0.1.1
- 完全重构。


### 0.0.1
- 上传代码。
 
 
