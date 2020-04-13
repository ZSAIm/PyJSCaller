# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from functools import wraps
import jscaller


def object2result(obj):
    """ Object 转 Result。"""
    return Result(obj.__parent__, obj.__name__, True)


def object2expr(obj):
    """ Object 转 Express。"""
    return Express(obj.__parent__, object2result(obj), None)


def expr_operation(func):
    """ 对 Object对象的运算，需要将其封装成结果单元Result才能参与运算。
    再由于每一个Result都需要Express进行封装，所以再加一层表达式单元Express。
    """
    @wraps(func)
    def wrapper(*args):
        args = list(args)
        for i, obj in enumerate(args):
            if isinstance(obj, Object):
                args[i] = object2expr(args[i])

        return func(*args)
    return wrapper


class BaseObject(object):
    """ 每一个表达式的运算生成的表达式都没有父级对象，"""

    @expr_operation
    def __add__(self, other):
        return Express(None, (self, other), '+')

    @expr_operation
    def __radd__(self, other):
        return Express(None, (other, self), '+')

    @expr_operation
    def __sub__(self, other):
        return Express(None, (self, other), '-')

    @expr_operation
    def __rsub__(self, other):
        return Express(None, (other, self), '-')

    @expr_operation
    def __mul__(self, other):
        return Express(None, (self, other), '*')

    @expr_operation
    def __rmul__(self, other):
        return Express(None, (other, self), '*')

    @expr_operation
    def __div__(self, other):
        return Express(None, (self, other), '/')

    @expr_operation
    def __rdiv__(self, other):
        return Express(None, (other, self), '*')

    @expr_operation
    def __divmod__(self, other):
        return Express(None, (other, self), '%')

    def __getattr__(self, item):
        return Object(self, item)

    __getitem__ = __getattr__


def array2result(list_tuple):
    """ list/tuple 转 Result。"""
    return Result(None, '[]', False, *list_tuple)


def dict2result(_dict):
    """ dict 转 Result。"""
    return Result(None, '{}', False, **_dict)


def array2expr(parent, list_tuple):
    """ list/tuple 转 Express。"""
    return Express(parent, array2result(list_tuple), None)


def dict2expr(parent, _dict):
    """ dict 转 Express。"""
    return Express(parent, dict2result(_dict), None)


class Object(BaseObject):
    """ 对象单元，作为中间对象的形式存在。这是为了避免对中间对象进行结果单元构建。 """
    def __init__(self, parent, name):
        self.__parent = parent
        self.__name = name

    @property
    def __parent__(self):
        return self.__parent

    @property
    def __name__(self):
        return self.__name

    def __call__(self, *args, **kwargs):
        """ 对象的函数调用必然需要作为一个结果单元进行运算。 """
        return Express(self.__parent, Result(self.__parent, self.__name, False, *args, **kwargs), None)

    def __repr__(self):
        return self.__origin_expr__()

    def __str__(self):
        return self.__origin_expr__()

    def __origin_expr__(self):
        if self.__parent:
            # 如果表达式是运算结果的时候，使用()把运算结果框起来。
            # 否则，以属性的形式引用加.
            if self.__parent__.__is_result__():
                parent_str = '%s.'
            else:
                parent_str = '(%s).'
            parent_str = parent_str % self.__parent.__origin_expr__()
        else:
            parent_str = ''

        return parent_str + self.__name


class Express(BaseObject):
    """ 表达式单元，用于存储构建结果的单元之间的关系。

    当 operands是Result结果对象的时候，说明这是作为函数调用的结果。
    而当operands是元组对象的时候，说明这是运算结果，loperand是左操作数，roperand是右操作数。
    """
    def __init__(self, parent=None, operands=None, operator=None):
        self.__parent = parent
        self.__operator = operator
        self.__operands = operands

        self._new = False

        self._value = None

    @property
    def __loperand__(self):
        return self.__operands[0]

    @property
    def __roperand__(self):
        return self.__operands[1]

    @property
    def __parent__(self):
        return self.__parent

    @property
    def __result__(self):
        return self.__operands

    def __new_instance__(self):
        self.__result__.__new_instance__()

    def __is_result__(self):
        """ 因为每一个结果单元Result都需要使用Express进行封装，所以有必要检测该表达式是否为结果单元。 """
        return isinstance(self.__operands, Result)

    def __call__(self, *args, **kwargs):
        if self.__is_result__():
            name = self.__result__.__name__
            parent = self.__parent
        else:
            name = '()'
            parent = self

        return Express(parent, Result(parent, name, False, *args, **kwargs))

    def get_value(self):
        """ """
        if self._value is not None:
            return self._value
        if self.__is_result__():
            self._value = self.__result__.get_value()
            return self._value
        else:
            eval_array = []
            for i in self.__operands:
                if isinstance(i, Express):
                    eval_array.append(i.get_value().__repr__())
                else:
                    eval_array.append(i.__repr__())
            try:
                res = eval(self.__operator.join(eval_array), {}, {})
            except Exception as e:
                raise RuntimeError('Express(%s): %s' % (self.__operator.join(eval_array), str(e)))
            self._value = res
            return res

    result = get_value

    def __linked_expr__(self, sess):
        """ 返回连接会话的结果对象后的表达式。 """
        if self.__is_result__():
            return '%s[%d]' % (jscaller.VARIABLE_NAME, sess.index(self.__result__))
        else:
            expr_array = []
            for i in self.__operands:
                expr_array.append(_determine_linked_expr(i, sess))

            return self.__operator.join(expr_array)

    def __origin_expr__(self):
        """ 返回表达式文本。 """
        if self.__is_result__():
            code = self.__result__.__origin_expr__()
            return code
        else:
            expr_array = []
            for i in self.__operands:
                expr_array.append(_determine_origin_expr(i))
            return '%s' % self.__operator.join(expr_array)

    def __repr__(self):
        return self.__origin_expr__()

    __str__ = __repr__


class Result(object):
    """ 结果单元是真正作为执行单元的对象。
    注意的是：每一个结果单元都需要使用表达式单元对象Express进行封装，
            这是为了实现让结果单元能够进行再次运算的操作。
    """
    def __init__(self, parent, object_name, is_attribute, *args, **kwargs):
        self.__parent = parent
        self.__name = object_name
        self.__args = []
        self.__kwargs = {}
        self.__isattr = is_attribute
        self.__new = False
        self.__value = None

        # 如果使用的是Object对象作为参数，那么意味着该对象应该作为结果进行处理。
        # 所以需要将其转化为Result对象。并且为了保持一致性，再使用表达式对象封装结果。
        for i in args:
            if type(i) in (list, tuple):
                app = array2expr(parent, i)
            elif type(i) is dict:
                app = dict2expr(parent, i)
            else:
                if isinstance(i, Object):
                    i = object2expr(i)
                app = i
            self.__args.append(app)

        for i, j in kwargs.items():
            if type(j) in (list, tuple):
                kw_value = array2expr(parent, j)
            elif isinstance(j, dict):
                kw_value = dict2expr(parent, j)
            else:
                # 对于Object对象需要将其转成Express
                if isinstance(j, Object):
                    j = object2expr(j)
                kw_value = j

            self.__kwargs[i] = kw_value

    @property
    def __parent__(self):
        return self.__parent

    def __new_instance__(self):
        self.__new = True

    def __value__(self, value):
        self.__value = value

    def get_value(self):
        return self.__value

    getValue = get_value

    def __linked_expr__(self, sess):
        """ 返回连接会话的结果对象后的表达式。 """
        # 字典结果对象和列表结果对象需要逐个元素进行格式化连接。
        if self.__name == '{}':
            # 字典对象：{**kwargs}
            return '{%s}' % _stringify_linked_dict_expr(self.__kwargs, sess)
        elif self.__name in '[]':
            # 列表对象：[*args]
            return '[%s]' % _stringify_linked_array_expr(self.__args, sess)
        elif self.__name == '()':
            # 缘由： (Express + Express)(...)
            return '(%s)(%s)' % (self.__parent.__linked_expr__(sess), _stringify_array_expr(self.__args))
        else:
            parent_str = ''
            if self.__parent:
                if isinstance(self.__parent, Object):
                    # Object对象作为静态属性，不需要进行搜索建立引用连接关系。
                    parent_str = self.__parent.__origin_expr__() + '.'
                else:
                    # 理论上来说，结果对象Result的父级剩下的只可能是Express对象
                    # 所以只需要将其交由表达式连接即可。
                    fm = '%s.'
                    if not isinstance(self.__parent.__result__, Result):
                        fm = '(%s).'
                    parent_str = fm % self.__parent.__linked_expr__(sess)

            new_str = ''
            if self.__new:
                new_str = 'new '
            if self.__isattr:
                return '{parent}{object_name}'.format(
                    parent=parent_str,
                    object_name=self.__name
                )
            else:
                return '{new}{parent}{object_name}({arguments})'.format(
                    new=new_str,
                    parent=parent_str,
                    object_name=self.__name,
                    arguments=_stringify_linked_array_expr(self.__args, sess)
                )

    def __origin_expr__(self):
        """ 返回表达式文本。 """
        if self.__name == '{}':
            # 字典对象：{**kwargs}
            return '{%s}' % _stringify_dict_expr(self.__kwargs)
        elif self.__name == '[]':
            # 列表对象：[*args]
            return '[%s]' % _stringify_array_expr(self.__args)
        elif self.__name == '()':
            # 缘由： (Express + Express)(...)
            return '(%s)(%s)' % (self.__parent.__origin_expr__(), _stringify_array_expr(self.__args))
        else:
            # 缘由： Express/Object.name(*args)
            parent_str = ''
            if self.__parent:
                # 如果是表达式的运算结果，那么使用()把运算结果框起来。
                if self.__parent.__is_result__():
                    parent_str = '%s.' % self.__parent.__origin_expr__()
                else:
                    parent_str = '(%s).' % self.__parent.__origin_expr__()

            new_str = ''
            if self.__new:
                new_str = 'new '

            if self.__isattr:
                return '{parent}{object_name}'.format(parent=parent_str, object_name=self.__name)
            else:
                return '{new}{parent}{object_name}({arguments})'.format(
                    new=new_str,
                    parent=parent_str,
                    object_name=self.__name,
                    arguments=_stringify_array_expr(self.__args)
                )

    def findall_expr(self):
        """ 搜索返回参数中所有的表达式对象。 """
        exprs = []
        for i in self.__args:
            if isinstance(i, Express):
                exprs.append(i)

        for i in self.__kwargs.values():
            if isinstance(i, Express):
                exprs.append(i)

        return exprs

    def __repr__(self):
        return self.__origin_expr__()

    __str__ = __repr__

    def __eq__(self, other):
        return id(other) == id(self)


def _stringify_array_expr(expr_args):
    """ 字符串化列表结果对象的Result。 """
    _args_str_array = []
    for i in expr_args:
        if isinstance(i, Express):
            _args_str_array.append((i.__origin_expr__(), True))
        else:
            _args_str_array.append((i, False))

    return ','.join([i[0].__repr__() if i[1] is False else i[0] for i in _args_str_array])


def _stringify_linked_array_expr(expr_args, sess):
    """ 字符串化连接了的列表结果对象Result。"""

    ret_expr_array = []
    for i in expr_args:
        ret_expr_array.append(_determine_linked_expr(i, sess))

    return ','.join(ret_expr_array)


def _stringify_dict_expr(expr_dict):
    """ 字符串化字典结果对象Result。 """
    _args_str = []
    for i, j in expr_dict.items():
        if isinstance(j, Express):
            data = i.__repr__(), j.__origin_expr__()
        else:
            data = i.__repr__(), j.__repr__()
        _args_str.append(data)
    _kwargs_str = ['%s:%s' % (i[0], i[1]) for i in _args_str]
    return ','.join(_kwargs_str)


def _stringify_linked_dict_expr(expr_dict, sess):
    """ 字符串化连接了的字典对象Result。"""
    _args_str = []
    for i, j in expr_dict.items():
        if isinstance(j, Express):
            data = i.__repr__(), j.__linked_expr__(sess)
        else:
            data = i.__repr__(), j.__repr__()
        _args_str.append(data)

    _kwargs_str = ['%s:%s' % (i[0], i[1]) for i in _args_str]
    return ','.join(_kwargs_str)


def _determine_origin_expr(expr):
    """ 返回由表达式决定的原表达式文本。"""
    if isinstance(expr, Express):
        return expr.__origin_expr__()
    else:
        return expr.__repr__()


def _determine_linked_expr(expr, sess):
    """ 返回由连接表达式决定的表达式文本。"""
    if isinstance(expr, Express):
        return expr.__linked_expr__(sess)
    else:
        return expr.__repr__()




