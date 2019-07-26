

__all__ = ["Object", "Express", "Result",
           "array_result", "dict_result", "require_object"]

JS_HANDLE_NAME = '_'


def require_object(parent, container, object_names=(), preobjs=()):
    objs = []
    for i in object_names:
        if i in container:
            objs.append(container[i])
            continue
        pt = parent
        if not isinstance(parent, Express) and not isinstance(parent, Object):
            pt = None
        obj = Object(pt, i, preobjs)
        container[i] = obj
        objs.append(obj)
        setattr(parent, i, obj)

    return objs if len(objs) > 1 else objs[0]


class Object:
    """ Express's and Result's Object

    """
    def __init__(self, parent, name: str, preobjs=()):
        self._parent = parent
        self._name = name
        self._objs = {}
        for i in preobjs:
            self._objs[i.name] = i
            setattr(self, i.name, i)
        self._subobj = list(preobjs)

    def sub(self, *subobj):
        self._subobj.extend(subobj)

    @property
    def parent(self):
        return self._parent

    @property
    def name(self):
        return self._name

    def __call__(self, *args, **kwargs):
        expr = Express(self._parent,
                       Result(self._parent, self._name, False, *args, **kwargs),
                       None,
                       self._subobj)

        return expr

    def get(self, *args):
        return require_object(self, self._objs, args)

    def __repr__(self):
        return self.getOriginExpr()

    def __str__(self):
        return self.getOriginExpr()

    def getOriginExpr(self):
        if self._parent:
            parent_str = self._parent.getOriginExpr() + '.'
        else:
            parent_str = ''
        return parent_str + self._name


class Express:
    """ Create a Express to be compiled by Session.

    """
    def __init__(self, parent=None, operands=None, operator=None,
                 preobjs=()):
        self._parent = parent
        self._operator = operator
        self._operands = operands

        self._objs = {}
        for i in preobjs:
            self.get(i.name)

        self._new = False

        if isinstance(operands, Result):
            self._is_result = True
        else:
            self._is_result = False

        self._value = None


    @property
    def parent(self):
        return self._parent

    @property
    def result(self):
        if not self._is_result:
            raise TypeError("%s isn't a Result." % self.getOriginExpr())

        return self._operands

    @property
    def operator(self):
        return self._operator

    def __contains__(self, item):
        if self._is_result:
            return False

        if isinstance(self.loperand, Express) or isinstance(self.roperand, Express):
            return True

        return False

    def __call__(self, *args, **kwargs):
        if not self._is_result:
            raise AttributeError("not type of Result")
        return Express(self._parent,
                       Result(self._parent, self.result.met_name, False, *args, **kwargs),
                       None)

    def isResult(self):
        return self._is_result

    @property
    def loperand(self):
        return self._operands[0]

    @property
    def roperand(self):
        return self._operands[1]

    def get(self, *args):
        return require_object(self, self._objs, args)

    def getValue(self):
        if self._value is not None:
            return self._value
        if self._is_result:
            self._value = self.result.getValue()
            return self._value
        else:
            eval_array = []
            for i in self._operands:
                if isinstance(i, Express):
                    eval_array.append(_expr_type_text(i.getValue()))
                else:
                    eval_array.append(_expr_type_text(i))
            try:
                res = eval(self.operator.join(eval_array))
            except Exception as e:
                raise RuntimeError('Express(%s): %s' % (self.operator.join(eval_array), str(e)))
            self._value = res
            return res

    def getLinkedExpr(self, sess):
        if self._is_result:
            return '%s[%d]' % (JS_HANDLE_NAME, sess.index(self.result))
        else:
            expr_array = []
            for i in self._operands:
                expr_array.append(_determine_linked_expr(i, sess))

            return self.operator.join(expr_array)

    def getOriginExpr(self):
        if self._is_result:
            code = self.result.getOriginExpr()
            return code
        else:
            expr_array = []
            for i in self._operands:
                expr_array.append(_determine_origin_expr(i))
            return '%s' % self.operator.join(expr_array)

    def __add__(self, other):
        return Express(None, (self, other), '+')

    def __radd__(self, other):
        return Express(None, (other, self), '+')

    def __sub__(self, other):
        return Express(None, (self, other), '-')

    def __rsub__(self, other):
        return Express(None, (other, self), '-')

    def __mul__(self, other):
        return Express(None, (self, other), '*')

    def __rmul__(self, other):
        return Express(None, (other, self), '*')

    def __div__(self, other):
        return Express(None, (self, other), '/')

    def __rdiv__(self, other):
        return Express(None, (other, self), '*')

    def __str__(self):
        return self.getOriginExpr()

    def __repr__(self):
        return self.getOriginExpr()


def _array_expr(parent, list_tuple):
    return Express(parent, array_result(list_tuple), None)


def _dict_expr(parent, _dict):
    return Express(parent, dict_result(_dict), None)


def array_result(list_tuple):
    return Result(None, '[]', False, *list_tuple)


def dict_result(_dict):
    return Result(None, '{}', False, **_dict)


class Result:
    """ Result is a Express that actually executes in JSEngine.

    """
    def __init__(self, parent, object_name: str, is_attribute: bool, *args, **kwargs):
        self._parent = parent
        self._obj_name = object_name
        self.args = []
        self.kwargs = {}
        self._isattr = is_attribute
        self._new = False
        self._value = None

        for i in args:
            if isinstance(i, list) or isinstance(i, tuple):
                app = _array_expr(parent, i)
            elif isinstance(i, dict):
                app = _dict_expr(parent, i)
            else:
                app = i
            self.args.append(app)

        for i, j in kwargs.items():
            if isinstance(j, list) or isinstance(j, tuple):
                kwvalue = _array_expr(parent, j)
            elif isinstance(j, dict):
                kwvalue = _dict_expr(parent, j)
            else:
                kwvalue = j

            self.kwargs[i] = kwvalue

    def __str__(self):
        return self.getOriginExpr()

    def __repr__(self):
        return self.getOriginExpr()

    def __eq__(self, other):
        return id(other) == id(self)

    def new(self):
        self._new = True

    def link(self, value):
        self._value = value

    def getValue(self):
        return self._value

    def getLinkedExpr(self, sess):
        if self._obj_name == '{}':
            return '{%s}' % _dict_js_expr(self.kwargs, sess)
        elif self._obj_name == '[]':
            return '[%s]' % _args_js_expr(self.args, sess)
        else:
            parent_str = ''
            if self._parent:
                if isinstance(self._parent, Object):
                    parent_str = self._parent.getOriginExpr() + '.'
                else:
                    parent_str = '%s[%d].' % (JS_HANDLE_NAME,
                                              sess.index(self._parent.result))
            new_str = ''
            if self._new:
                new_str = 'new '
            if self._isattr:
                return '{parent}{object_name}'.format(
                    parent=parent_str,
                    object_name=self._obj_name
                )
            else:
                return '{new}{parent}{object_name}({arguments})'.format(
                    new=new_str,
                    parent=parent_str,
                    object_name=self._obj_name,
                    arguments=_args_js_expr(self.args, sess)
                )

    def getOriginExpr(self):
        if self._obj_name == '{}':
            return '{%s}' % _dict_origin_expr(self.kwargs)
        elif self._obj_name == '[]':
            return '[%s]' % _args_origin_expr(self.args)
        else:
            parent_str = self._parent.getOriginExpr() + '.' if self._parent else ''

            new_str = ''
            if self._new:
                new_str = 'new '

            if self._isattr:
                return '{parent}{object_name}'.format(
                    parent=parent_str,
                    object_name=self._obj_name
                )
            else:
                return '{new}{parent}{object_name}({arguments})'.format(
                    new=new_str,
                    parent=parent_str,
                    object_name=self._obj_name,
                    arguments=_args_origin_expr(self.args)
                )

    def findAllExpr(self):
        exprs = []
        for i in self.args:
            if isinstance(i, Express):
                exprs.append(i)

        for i in self.kwargs.values():
            if isinstance(i, Express):
                exprs.append(i)

        return exprs


def _expr_type_text(expr):
    return expr.__repr__()


def _args_origin_expr(expr_args):
    _args_str_array = []
    for i in expr_args:
        if isinstance(i, Express):
            _args_str_array.append((i.getOriginExpr(), True))
        else:
            _args_str_array.append((i, False))

    return ','.join([_expr_type_text(i[0]) if i[1] is False else i[0] for i in _args_str_array])


def _args_js_array(expr_args, sess):
    ret_expr_array = []
    for i in expr_args:
        ret_expr_array.append(_determine_linked_expr(i, sess))

    return ret_expr_array


def _args_js_expr(expr_args, sess):
    return ','.join(_args_js_array(expr_args, sess))


def _dict_origin_expr(expr_dict):
    _args_str = []
    for i, j in expr_dict.items():
        if isinstance(j, Express):
            data = _expr_type_text(i), j.getOriginExpr()
        else:
            data = _expr_type_text(i), _expr_type_text(j)
        _args_str.append(data)
    _kwargs_str = ['%s:%s' % (i[0], i[1]) for i in _args_str]
    return ','.join(_kwargs_str)


def _dict_js_expr(expr_dict, sess):
    _args_str = []
    for i, j in expr_dict.items():
        if isinstance(j, Express):
            data = _expr_type_text(i), j.getLinkedExpr(sess)
        else:
            data = _expr_type_text(i), _expr_type_text(j)
        _args_str.append(data)

    _kwargs_str = ['%s:%s' % (i[0], i[1]) for i in _args_str]
    return ','.join(_kwargs_str)


def _determine_origin_expr(expr):
    if isinstance(expr, Express):
        return expr.getOriginExpr()
    else:
        return _expr_type_text(expr)


def _determine_linked_expr(expr, sess):
    if isinstance(expr, Express):
        return expr.getLinkedExpr(sess)
    else:
        return _expr_type_text(expr)










