# -*- coding: UTF-8 -*-
from tempfile import NamedTemporaryFile
from traceback import print_exc
from os import unlink, path
from .express import Express, Result, Object
from .express import dict2result, array2result, object2result
import jscaller
from .engine import NodeJS

import json

GLOBAL_JSENGINE = NodeJS


class JSContext:
    def __init__(self, file, timeout=None, engine=None):
        with open(file, 'r') as f:
            self._js_context = f.read()
        self.timeout = timeout
        self.engine = engine

    def call(self, name, *args):
        """ 调用JS脚本函数。 """
        with Session(self._js_context, self.timeout, self.engine) as sess:
            obj = sess.get(name)
            ret = sess.call(obj(*args))
        return ret.get_value()


class Session:
    def __init__(self, js_context='', timeout=None, engine=None):
        """
        :param
            js_context  : JS上下文脚本。
            timeout     : 引擎的超时执行参数，如果为指定则无限等待。
            engine      : 执行引擎对象，不指定的话使用全局设定
        """
        self._exec_expr = []
        self._result_cells = []
        self._exec_results = None
        self._timeout = timeout
        self._drive_code = ''
        self.js_ctx = js_context
        if not engine:
            engine = GLOBAL_JSENGINE
        self.engine = engine
        self._closed = False

        self.process = None

    def shutdown(self):
        if not self.process:
            raise RuntimeError('cannot shutdown a idle session.')
        self.process.terminate()

    def close(self):
        self._closed = True

    def __enter__(self):
        return self

    def enter(self):
        """ 进入会话。 """
        return self.__enter__()

    def index(self, result):
        """ 索引结果对象。 """
        return self._result_cells.index(result)

    def leave(self):
        """ 结束会话。 """
        self.run()
        self.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print_exc()
        else:
            self.leave()

    def run(self):
        """ 运行JS执行引擎。"""
        for i in self._exec_expr:
            self._extract_expr_result_chain_(i)

        drv_code = self.compile()
        pipe_res = self._exec_(drv_code)

        self._unwrap_(pipe_res)

    def _unwrap_(self, pipe_res):
        """ 分发执行结果。 """
        for i, result in enumerate(self._result_cells):
            result.__value__(pipe_res[i])

        self._exec_results = pipe_res

    def _exec_(self, drv_code):
        """ 调用执行JS代码。 """
        self._drive_code = drv_code
        with NamedTemporaryFile(mode='w', prefix='jsc_', suffix='.js', delete=False) as temp:
            with open(temp.name, 'w') as tmpf:
                tmpf.write(self.js_ctx + drv_code)
            # 调用JS执行引擎。
            res = self._run_pipe(temp.name)
        unlink(temp.name)

        return json.loads(res.split('\n\t\n\t')[-2])

    def _run_pipe(self, js_code):
        """ 管道调用运行时引擎。"""
        process, stdout, stderr = self.engine.execute(js_code, self._timeout)
        if stderr or not stdout:
            raise RuntimeError(stderr)

        self.process = process

        return stdout

    def _extract_result_(self, res):
        """ 提取结果对象。"""
        assert isinstance(res, Result)

        # 搜索结果对象的所有表达式对象进行逐级往下提取。
        # 对于结果对象使用到的每一个表达式都需要进行完全提取。
        exprs = res.findall_expr()

        for i in exprs:
            self._extract_expr_result_chain_(i)

        if res not in self._result_cells:
            self._result_cells.append(res)

    def _extract_expr_result_chain_(self, expr):
        """ 完全提取表达式的结果链。 """
        # Object对象定义为结果Result或者Express的链式中间对象，所以不需要对其进行提取其结果链。
        if not isinstance(expr, Object):
            if expr.__is_result__():

                # 由于传递进来的表达式是属于表达式的底端，所以需要先完全提取父级对象的结果链。
                # 这里使用递归的方法，所以实际上的提取流程会变成：
                #   1. 从顶端父级开始进行提取结果对象。
                #   2. 然后逐级往下提取结果。
                #   3. 这就保证了结果对象在连接时候有正确的先后顺序。
                # 总的来说：整个流程就是先通过父级递进到顶端，然后再通过extract_result往下提取结果。
                if expr.__parent__:
                    self._extract_expr_result_chain_(expr.__parent__)

                if expr.__result__ not in self._result_cells:
                    self._extract_result_(expr.__result__)
            else:
                # 如果是表达式的运算结果，那么需要单独为两个操作数提取结果对象。
                if isinstance(expr.__loperand__, Express):
                    self._extract_expr_result_chain_(expr.__loperand__)

                if isinstance(expr.__roperand__, Express):
                    self._extract_expr_result_chain_(expr.__roperand__)

    def call(self, *exprs):
        """ 提交被转化翻译执行的对象给执行会话。 """
        ret_expr = []
        for expr in exprs:
            if isinstance(expr, Express):
                # 作为表达式对象Express，
                if expr not in self._exec_expr:
                    self._exec_expr.append(expr)
                ret_expr.append(expr)
            else:
                # 如果是作为列表或字典进行call的话，那么会检查其中的所有的对象,
                # 并将其使用Express包装为结果Result对象
                if isinstance(expr, dict):
                    _kwarg_expr = {}
                    for i, j in expr.items():
                        if type(i) in (list, dict, tuple):
                            _kwarg_expr[i] = self.call(j)
                        else:
                            _kwarg_expr[i] = j
                    res = dict2result(_kwarg_expr)
                elif type(expr) in (list, tuple):
                    _args_expr = []
                    for i in expr:
                        if type(i) in (list, dict, tuple):
                            _args_expr.append(self.call(i))
                        else:
                            _args_expr.append(i)
                    res = array2result(_args_expr)
                elif isinstance(expr, Object):
                    # 对于对象Object，那么需要将将其作为Result对象才能让其作为执行单元。
                    res = object2result(expr)
                else:
                    res = expr

                _expr = Express(None, res, None)
                ret_expr.append(_expr)
                self._exec_expr.append(_expr)

        if len(ret_expr) == 1:
            return ret_expr[0]

        return ret_expr

    def compile(self):
        """
            {... prefix code ...}

            var VARIABLE_NAME = [];

            VARIABLE_NAME.push(...);
            ...

            console.log('\n\t\n\t' + JSON.stringify(VARIABLE_NAME) + '\n\t\n\t');

            {... suffix code ...}
        """

        exec_cells = []
        for i in self._result_cells:
            value = i.__linked_expr__(self)
            exec_cells.append('%s.push(%s);\n' % (jscaller.VARIABLE_NAME, value))

        # 使用双分隔符来包围输出结果。
        template = '{prefix};'\
                   'var {name}=[];'\
                   '{exec_cells};' \
                   'console.log("{seperator}"+JSON.stringify({name})+"{seperator}");' \
                   '{suffix};'

        return template.format(seperator=r'\n\t\n\t',
                               name=jscaller.VARIABLE_NAME,
                               exec_cells=str(''.join(exec_cells)),
                               prefix=self.engine.prefix,
                               suffix=self.engine.suffix)

    @staticmethod
    def get(*args):
        """ 获取JS脚本上下文。 """
        objs = []
        for i in args:
            o = Object(None, i)
            objs.append(o)

        return objs if len(objs) > 1 else objs[0]

    def __repr__(self):
        return '<Session %s>' % path.join(self.engine.source, self.engine.name)
