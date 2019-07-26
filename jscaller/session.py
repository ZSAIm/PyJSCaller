
from tempfile import NamedTemporaryFile
from traceback import print_exc
from ._compatiable import PY2, PY3
from os import unlink
from jscaller.express import Express, Result, Object, require_object
from jscaller.express import dict_result, array_result

from jscaller.engine import NodeJS
from jscaller.collect import OBJECT

import json

JS_HANDLE_NAME = '_'
RUNTIME_JSENGINE = NodeJS

class Session:
    def __init__(self, fscript=None, timeout=None):
        self._objs = {}
        self._exec_expr = []
        self._results = []
        self._file = fscript
        self._full_res = None
        self._timeout = timeout

        self.closed = False

        self.proc = None


    def close(self):
        self.closed = True

    def __enter__(self):
        return self

    def enter(self):
        return self.__enter__()

    def index(self, result):
        return self._results.index(result)

    def leave(self):
        self.run()
        self.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print_exc()
        else:
            self.leave()

    def get(self, *args):
        objs = []
        for i in args:
            if i in self._objs:
                o = self._objs[i]
            elif i in OBJECT:
                o = OBJECT[i]
                self._objs[i] = o
            else:
                o = require_object(self, self._objs, [i])
            objs.append(o)

        return objs if len(objs) > 1 else objs[0]

    def run(self):
        if self._full_res:
            return

        for i in self._exec_expr:
            self._extract_expr_(i)

        drv_code = self.compile()
        pipe_res = self._exec_(drv_code)

        self._unwrap_(pipe_res)

    def _unwrap_(self, pipe_res):
        for i, result in enumerate(self._results):
            result.link(pipe_res[i])

        self._full_res = pipe_res

    def _exec_(self, drv_code):
        with NamedTemporaryFile(mode='w', prefix='jscaller_', suffix='.js', delete=False) as temp:
            with open(temp.name, 'w') as tmpf:
                if self._file:
                    with open(self._file, 'r') as codef:
                        tmpf.write(codef.read() + drv_code)
                else:
                    tmpf.write(drv_code)

            res = self._run_pipe(temp.name)
        unlink(temp.name)

        return json.loads(res.split('\n\t\n\t')[-1])

    def _run_pipe(self, fscript):
        proc = RUNTIME_JSENGINE.Popen(fscript)
        self.proc = proc

        if PY3:
            if self._timeout:
                timeout = self._timeout
            else:
                timeout = RUNTIME_JSENGINE.timeout
            stdout, stderr = proc.communicate(timeout=timeout)
        elif PY2:
            stdout, stderr = proc.communicate()
        else:
            raise AssertionError('Not Compatible Version Of Python.')

        if stderr:
            raise RuntimeError(stderr)
        if not stdout:
            raise RuntimeError('')

        return stdout

    def _extract_parent_(self, expr):
        if not isinstance(expr, Object):
            if expr.parent:
                self._extract_parent_(expr.parent)

            if expr.result not in self._results:
                self._results.append(expr.result)

    def _extract_result_(self, res):
        if isinstance(res, Result):
            exprs = res.findAllExpr()

            for i in exprs:
                self._extract_expr_(i)

        if res not in self._results:
            self._results.append(res)

    def _extract_expr_(self, expr):
        if expr.isResult():
            self._extract_parent_(expr)
            bak = self._results.pop()
            self._extract_result_(expr.result)
            if bak not in self._results:
                self._results.append(bak)
        else:
            if isinstance(expr.loperand, Express):
                self._extract_expr_(expr.loperand)
            if isinstance(expr.roperand, Express):
                self._extract_expr_(expr.roperand)

    def _make_dict_expr(self, expr):
        _kwarg_expr = {}
        for i, j in expr.items():
            if isinstance(j, list) or isinstance(j, dict):
                _kwarg_expr[i] = self.call(j)
            else:
                _kwarg_expr[i] = j
        return dict_result(_kwarg_expr)

    def _make_array_expr(self, expr):
        _args_expr = []
        for i in expr:
            if isinstance(i, list) or isinstance(i, dict):
                _args_expr.append(self.call(i))
            else:
                _args_expr.append(i)
        return array_result(_args_expr)

    def call(self, expr):
        """
            Pass Express to Session.
        """
        if isinstance(expr, Express):
            if expr not in self._exec_expr:
                self._exec_expr.append(expr)
            return expr
        else:
            if isinstance(expr, dict):
                res = self._make_dict_expr(expr)
            elif isinstance(expr, list) or isinstance(expr, tuple):
                res = self._make_array_expr(expr)
            elif isinstance(expr, Object):
                res = Result(expr.parent, expr.name, True)
            else:
                res = expr

            _expr = Express(None, res, None)
            self._exec_expr.append(_expr)
            return _expr


    def compile(self):
        """
            {... prefix code ...}

            var JS_HANDLE_NAME = [];

            JS_HANDLE_NAME.push(...);
            ...

            console.log('\r\n\r\n');

            console.log(JSON.stringify(JS_HANDLE_NAME));
            {... suffix code ...}
        """

        exec_cells = []
        for i in self._results:
            value = i.getLinkedExpr(self)
            exec_cells.append('%s.push(%s);\n' % (JS_HANDLE_NAME, value))

        template = ';{prefix};'\
                   'var {name}=[];'\
                   '{exec_cells};' \
                   '{seperator};' \
                   'console.log(JSON.stringify({name}));'\
                   '{suffix};'

        return template.format(seperator='console.log("\\n\\t\\n\\t")',
                               name=JS_HANDLE_NAME,
                               exec_cells=str(''.join(exec_cells)),
                               prefix=RUNTIME_JSENGINE.prefix,
                               suffix=RUNTIME_JSENGINE.suffix)
