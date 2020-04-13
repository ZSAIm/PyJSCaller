# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
__all__ = ["JSEngine", ]

from subprocess import PIPE, Popen

try:
    # py3
    from subprocess import TimeoutExpired
except ImportError:
    pass

from ._compatiable import PY2, PY3
from threading import Timer, Event
import os


class RuntimeTimeout(Exception):
    def __init__(self, command, timeout):
        self.cmd = command
        self.timeout = timeout


class JSEngine:
    """ 运行时JS引擎容器。

    :param
        name    : 运行时文件名
        cmd_args: 执行JS脚本文件所需的参数。
        source  : JS引擎的文件路径目录名称，若使用的是环境定义的运行时引擎则不需要指定。
        version : JS引擎的版本号
        timeout : 指定引擎执行的超时时间。
        prefix  : 引擎执行所需的预备准备工作代码。
        suffix  : 引擎执行的后续工作代码。


    以下参数属于subprocess.Popen的特性：
        encoding: Text mode encoding to use for file objects stdin, stdout and stderr.
        shell   : If true, the command will be executed through the shell.
        env     : Defines the environment variables for the new process.
        cwd     : Sets the current directory before the child is executed.


    """

    def __init__(self, name, cmd_args=(), source='',
                 version=None, encoding=None, shell=False,
                 timeout=None, prefix='', suffix='',
                 env=None, cwd=None,):

        self.version = version

        self.prefix = prefix
        self.suffix = suffix

        self.name = name
        self.cmd_args = list(cmd_args)
        self.source = source
        self.timeout = timeout

        self.encoding = encoding
        self.shell = shell

        self.env = env
        self.cwd = cwd

    def run(self, args=(), timeout=None):
        def timeout_check():
            """ 超时监控线程。 """
            # 超时后如果进程依然在运行中，那么将会杀掉进程。
            if process.poll() is None:
                kill_event.set()
                process.terminate()

        if self.shell:
            command = '{engine} {args}'.format(
                engine=os.path.join(self.source, self.name),
                args=' '.join(args)
            ).strip()
        else:
            command = [
                os.path.join(self.source, self.name),
            ]
            command.extend(args)

        timeout = timeout or self.timeout

        if PY2:
            process = Popen(command, shell=self.shell, stdout=PIPE, stderr=PIPE,
                            cwd=self.cwd, env=self.env)

            # 为了实现py2的子进程通信超时功能。使用定时线程来监控
            # 启动定时线程，若超时为完成，那么将会强制杀死进程。
            t = Timer(timeout, timeout_check)
            t.start()
            kill_event = Event()
            stdout, stderr = process.communicate()
            # 如果定时线程未启动说明未超时，可以取消定线程。
            t.cancel()
            if kill_event.is_set():
                raise RuntimeTimeout(command, timeout)
        else:
            process = Popen(command, encoding=self.encoding, shell=self.shell,
                            stdout=PIPE, stderr=PIPE, cwd=self.cwd, env=self.env)

            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except TimeoutExpired as e:
                raise RuntimeTimeout(e.cmd, e.timeout)

        return process, stdout, stderr

    def execute(self, file, timeout=None):
        """ 执行JS脚本。"""
        args = list(self.cmd_args)
        args.append(file)
        return self.run(args, timeout)

    def test(self, test_args=('--version',), timeout=None):
        """ JS引擎测试。返回JS引擎版本号。"""
        process, stdout, stderr = self.run(test_args, timeout=timeout)

        self.version = stdout.strip()
        return self.version

    def config(self, **kwargs):
        """ Configure the environment of Engine .

        Arguments:
            timeout, source, cmd_args, shell, cwd, env, encoding

        """
        for i, j in kwargs.items():
            if hasattr(self, i):
                setattr(self, i, j)

    def __repr__(self):
        return '<JSEngine %s>' % self.name
