PyJSCaller
===============

Run JavaScript code from Python.

PyJSCaller is a agent between Python and JavaScript making JavaScript involved in a more Python-like language.

a short example:

*****

	example.js


.. code::

	function add(a, b){
		return a + b;
	}

Supported JSEngine
====================

* `NodeJS <https://nodejs.org/>`_ - defalut
* `PhantomJS <https://phantomjs.org/>`_


Installation
===============

    $ pip install PyJSCaller


Example
=========

Usage1
~~~~~~~

.. code::

    >>> import jscaller
    >>> jscaller.eval("'Hello World!'.toUpperCase()")
    'HELLO WORLD!'

Usage2
~~~~~~~

.. code::

    >>> ctx = jscaller.compile('example.js', timeout=3)
    >>> ctx.call('add', 1, 1)
    2

Usage3
~~~~~~~

.. code::

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


Change JSEngine
~~~~~~~~~~~~~~~~~~

.. code::

    >>> from jscaller.engine import PhantomJS
    >>> PhantomJS.test()
    2.1.1
    >>> PhantomJS.config(timeout=10)
    >>> jscaller.make(PhantomJS)
    >>> jscaller.eval('1+1')
    2






License
===============
MIT license








