# -*- coding: utf-8 -*-

"""r
Run JavaScript code from Python.

PyJSCaller is a agent between Python and JavaScript,
makes JavaScript involved in a more Python-like language.

a short example:

--- example.js ------------------
 function add(a, b){
    return a + b;
 }
---------------------------------

>>> import jscaller
>>> jscaller.eval("'Hello World!'.toUpperCase()")
'HELLO WORLD!'
>>> from jscaller.collect import new, Date
>>> with jscaller.Session('example.js', timeout=3) as sess:
...     today = new(Date()).getFullYear()
...     sess.call(today)
...     add = sess.get('add')
...     retval = add(add(1, 2), 2)
...     sess.call(retval)
>>> retval.getValue()
5
>>> today.getValue()
2019

"""

__all__ = ["engine", "collect", "Session", "make", "eval"]

from . import engine, session, collect
from .session import Session


def make(engine):
    """ make the JS Execute Engine.
    """
    session.RUNTIME_JSENGINE = engine


def eval(jscode, timeout=None):
    with Session(timeout=timeout) as sess:
        retval = sess.call(collect.eval(jscode))
    return retval.getValue()

