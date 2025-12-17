# coding: utf-8

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime as DateTime

from distutils.dist import Distribution
from setuptools.command.build_ext import build_ext as SetupToolsBuildExt


_version = "0.4.0"

try:
    import ziglang
    zig_dir = Path(ziglang.__file__).parent
    os.environ['PATH'] = str(zig_dir) + ':' + os.environ['PATH']
    sys.path.insert(0, str(zig_dir))
except Exception:
    zig_dir = None


class ZigCompilerError(Exception):
    """Some compile/link operation failed."""


class Debug:
    def __init__(self):
        self.first_time = True
        self.verbose = None
        try:
            vbs = os.environ['SETUPTOOLS_ZIG_VERBOSE']
            # self.print('getting setuptools')
            self.verbose = int(vbs)
        except KeyError:
            # self.print('>>> keyerror SETUPTOOLS_ZIG_VERBOSE')
            pass
        except ValueError:
            self.print(f'cannot interpret "{vbs}" as integer')
        if self.verbose is None:
            if '-v' in sys.argv:
                self.verbose = 1
            elif '-vv' in sys.argv:
                self.verbose = 2
            else:
                self.verbose = 0

    def print(self, *args):
        if self.verbose == 0:
            return
        with Path('/tmp/setuptools_zig_debug.txt').open('a') as fh:
            if self.first_time:
                self.first_time = False
                print(f'\n\n{DateTime.now().replace(microsecond=0)} setuptools_zig: {_version}\n', file=fh)
            print(*args, file=fh)

    def __call__(self, *args):
        return self.print(*args)


debug = Debug()

# ext attributes:
#   define_macros
#   depends
#   export_symbols
#   extra_compile_args
#   extra_link_args
#   extra_objects
#   include_dirs
#   language
#   libraries
#   library_dirs
#   name
#   optional
#   py_limited_api
#   runtime_library_dirs
#   sources
#   swig_opts
#   undef_macros


class BuildExt(SetupToolsBuildExt):
    def __init__(self, dist, zig_value):
        self._zig_value = zig_value
        super().__init__(dist)

    def build_extension(self, ext):
        if not self._zig_value:
            return super().build_extension(ext)
        # debug(f'{debug.verbose=}')

        # check if every file in ext.sources exists
        for p in ext.sources:
            assert Path(p).exists()

        target = Path(self.get_ext_fullpath(ext.name))
        target.parent.mkdir(exist_ok=True, parents=True)  # subdir of build, not created by zig

        zig = os.environ.get('PY_ZIG', 'zig')  # override zig in path with specific version
        bld_cmd = [
           zig,
           'build-lib',
           '-dynamic',
           '-fallow-shlib-undefined',  # if not specified you have to provide -L and -lpythonX.Y otherwise undefined symbols
           f'-femit-bin={target}',
            '-lc',
        ]
        for inc_dir in self.compiler.include_dirs:
            bld_cmd.extend(('-I', inc_dir))
        for path in [
            '/usr/include',  # needed for docker compilation
            # '/usr/include/x86_64-linux-gnu/',  # cannot find how to get this from sysconfig or platform
        ]:
            if path in self.compiler.include_dirs:
                continue
            if os.path.exists(path):
                bld_cmd.extend(('-I', path))
        for path in Path('/usr/include').glob('*-linux-gnu'):
            bld_cmd.extend(('-I', str(path)))
        if '-O' not in ext.extra_compile_args:
            bld_cmd.extend(('-O', 'ReleaseFast'))
        bld_cmd.extend(ext.extra_compile_args)
        bld_cmd.extend(ext.sources)
        if debug.verbose > 1:
            debug('ext:')
            for elem in dir(ext):
                if elem and (elem[0] != '_'):
                    debug(f' {elem} -> {getattr(ext, elem)}')
            debug('compiler:')
            for k, v in self.compiler.__dict__.items():
                debug(f' {k} -> {v}')
        debug('cmd',  " ".join([x if " " not in x else '"' + x + '"' for x in bld_cmd]))
        sys.stdout.flush()
        res = subprocess.run(bld_cmd, capture_output=True, encoding='utf-8')
        if res.returncode != 0:
            print('\nrun return:\n', res)
            print('\n')
            raise ZigCompilerError(res.stderr)
        debug('res:', res)
        debug('\ntarget:', [str(target)])
        debug('found:', [str(x) for x in target.parent.glob('*')])


class ZigBuildExtension:
    def __init__(self, value):
        self._value = value

    def __call__(self, dist):
        return BuildExt(dist, zig_value=self._value)


def setup_build_zig(dist, keyword, value):
    assert isinstance(dist, Distribution)
    assert keyword == 'build_zig'
    be = dist.cmdclass.get('build_ext')
    dist.cmdclass['build_ext'] = ZigBuildExtension(value)
