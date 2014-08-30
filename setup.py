try:
    from cx_Freeze import setup, Executable
except ImportError:
    pass

import sys

base = 'Win32GUI' if sys.platform=='win32' else None

sys.path.append("pingpung")
buildOptions = dict(path=sys.path,
                    include_files=["pingpung/data"],
                    icon='pingpung/data/icon.ico',
                    excludes = ["tkinter"],
                    base = base)

executables = [
    Executable('pingpung/pingpung.py', base=base)
]

setup(name='PingPung',
      version = '0.0.3',
      description = 'Python3/QT4 Multiplatform Ping Application',
      options = dict(build_exe = buildOptions),
      executables = executables,
)
