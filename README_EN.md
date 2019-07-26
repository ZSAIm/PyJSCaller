PyJSCaller
===============
![Build Status](https://img.shields.io/badge/build-passing-green.svg)

Run JavaScript code from Python.

PyJSCaller is a agent between Python and JavaScript making JavaScript involved in a more Python-like language.

a short example:

*****

> example.js
    
```javascript
 function add(a, b){
    return a + b;
 }
```

##### Usage

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

# Supported JSEngine 

* [NodeJS](https://nodejs.org/) - defalut
* [PhantomJS](https://phantomjs.org/)


# Installation

    $ pip install PyJSCaller

# More Examples

Another short example

```python
>>> from jscaller.collect import new, String
>>> with jscaller.Session() as sess:
...     string = new(String("Hello JavaScript!"))
...     string.replace('JavaScript', 'Python')
...     sess.call(string)
>>> string.getValue()
"Hello Python!"
```

Using ``jscaller.make()`` to equip other JSEngine: 

```python
>>> from jscaller.engine import NodeJS, PhantomJS
>>> PhantomJS.environ(shell=True, timeout=5)
>>> jscaller.make(PhantomJS)
>>> jscaller.eval('1+1*2/4')
1.5
```

You can use ``PhantomJS.test()`` to check if engine worked correctly. 
```python
>>> PhantomJS.test()    # return the version number of PhantomJS
2.1.1 
```


# License
MIT license

# Changelog

### 0.1.0
- Rebuilt all.
- Linux was supported.
- Python 3.7.x was supported.
- Python 2.7.x was supported. 

### 0.0.1
- Uploaded code.
 
 