# -*- coding: UTF-8 -*-

r"""
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
>>> from jscaller import new, session
>>> with session('example.js', timeout=3) as sess:
...     Date, add = sess.get('Date', 'add')
...     today = new(Date()).getFullYear()
...     retval = add(add(1, 2), 2)
...     sess.call(today, retval)
>>> retval.get_value()
5
>>> today.get_value()
2019

"""

from __future__ import unicode_literals

from . import engine
from .session import Session, JSContext
from contextlib import contextmanager

__all__ = ["session", "engine", "Session", "make", "eval", "new"]


VARIABLE_NAME = '_'


def new(expr):
    """ 使用new运算符。"""
    expr.__new_instance__()
    return expr


def make(engine):
    """ 指定默认的JS执行引擎。"""
    session.GLOBAL_JSENGINE = engine


@contextmanager
def session(file, timeout=None, engine=None):
    """ 建立脚本会话。 """
    with open(file, 'r') as f:
        js_ctx = f.read()
    sess = Session(js_ctx, timeout, engine)
    yield sess
    sess.leave()


def eval(js_code, timeout=None, engine=None):
    """ 执行JS代码。"""
    with Session(js_code, timeout, engine) as sess:
        eval = sess.get('eval')
        retval = sess.call(eval(js_code))
    return retval.get_value()


def compile(js_file, timeout=None, engine=None):
    """ 生成JS上下文对象。 """
    return JSContext(js_file, timeout, engine)


