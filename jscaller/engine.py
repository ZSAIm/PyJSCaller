# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
__all__ = ['NodeJS', 'PhantomJS', 'JSEngine']

from ._engine import JSEngine


NodeJS = JSEngine(
    name='node',
    shell=True,
    encoding='utf-8',
)

PhantomJS = JSEngine(
    name='phantomjs',
    shell=True,
    encoding='utf-8',
    suffix='phantom.exit()',
)


