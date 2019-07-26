PyJSCaller
===============
[![Build Status](https://img.shields.io/badge/build-passing-green.svg)](https://github.com/ZSAIm/PyJSCaller)
[![Build Status](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/PyJSCaller/)


[Click here](https://github.com/ZSAIm/PyJSCaller/blob/master/README_EN.md) for the English version. 

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

##### 用法

```python
>>> import jscaller
>>> jscaller.eval("'Hello World!'.toUpperCase()")
'HELLO WORLD!'
>>> with jscaller.Session('example.js', timeout=3) as sess:
...     add = sess.get('add')
...     retval = add(add(1, 2), 2)
...     sess.call(retval)
>>> retval.getValue()
5
```


# 支持的JS引擎

* [NodeJS](https://nodejs.org/) - 默认
* [PhantomJS](https://phantomjs.org/)


# 安装

    $ pip install PyJSCaller

# 更多例子

另一个简短的例子。

```python
>>> from jscaller.collect import new, String
>>> with jscaller.Session() as sess:
...     string = new(String("Hello JavaScript!"))
...     string.replace('JavaScript', 'Python')
...     sess.call(string)
>>> string.getValue()
"Hello Python!"
```

使用 ``jscaller.make()`` 来装载别的JS引擎。

```python
>>> from jscaller.engine import NodeJS, PhantomJS
>>> PhantomJS.environ(shell=True, timeout=5)
>>> jscaller.make(PhantomJS)
>>> jscaller.eval('1+1*2/4')
1.5
```

使用 ``PhantomJS.test()`` 来测试引擎是否可以正常使用。

```python
>>> PhantomJS.test()    # return the version number of PhantomJS
2.1.1
```


# 许可证
MIT license

# 更新日志

### 0.1.0
- 完全重构。
- 支持 Linux。
- 支持 Python 3.7.x。
- 支持 Python 2.7.x。

### 0.0.1
- 上传代码。
 
 