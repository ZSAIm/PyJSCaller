

__all__ = ["JSEngine"]

from subprocess import PIPE, Popen
from ._compatiable import PY2, PY3
import os


class JSEngine:
    """ Runtime JSEngine Container.

    Arguments:
        name: Runtime name.

        cmd_args: Specify script file argument.

        source: JSEngine source path.

        version: Engine version, not actually necessary.

        encoding: Text mode encoding to use for file objects stdin,     ( subprocess.Popen -> encoding)
                stdout and stderr.

        shell: If true, the command will be executed through the shell. ( subprocess.Popen -> shell )

        timeout: Set runtime execute timeout.

        prefix: Preprocess before execute unit code.

        suffix: Postprocess after return unit.

        env: Defines the environment variables for the new process.     ( subprocess.Popen -> env   )

        cwd: Sets the current directory before the child is executed.   ( subprocess.Popen -> cwd   )


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

    def Popen(self, fscript):
        arg = [fscript]
        arg.extend(self.cmd_args)
        return self._Popen(arg)

    def _Popen(self, args):
        if self.shell:
            command = '{engine_filepath} {args}'.format(
                engine_filepath=os.path.join(self.source, self.name),
                args=' '.join(args)
            ).strip()
        else:
            command = [
                os.path.join(self.source, self.name),
            ]
            command.extend(args)

        if PY3:
            proc = Popen(command,
                         encoding=self.encoding,
                         shell=self.shell,
                         stdout=PIPE,
                         stderr=PIPE,
                         cwd=self.cwd,
                         env=self.env
                         )

        elif PY2:
            proc = Popen(command,
                         shell=self.shell,
                         stdout=PIPE,
                         stderr=PIPE,
                         cwd=self.cwd,
                         env=self.env
                         )
        else:
            raise AssertionError('Not Compatible Version Of Python.')

        return proc

    def test(self):
        proc = self._Popen(['--version'])

        if PY3:
            stdout, stderr = proc.communicate(timeout=self.timeout)
        elif PY2:
            stdout, stderr = proc.communicate()
        else:
            raise AssertionError('Not Compatible Version Of Python.')

        if stderr:
            raise RuntimeError(stderr)
        if not stdout:
            raise RuntimeError('')

        self.version = stdout.strip()
        return self.version

    def environ(self, **kwargs):
        """ Configure the environment of Engine .

        Arguments:
            timeout, source, cmd_args, shell, cwd, env, encoding

        """
        for i, j in kwargs.items():
            if hasattr(self, i):
                setattr(self, i, j)