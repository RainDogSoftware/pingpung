try:
    from cx_Freeze import setup, Executable
    executables = [Executable('pingpung/pingpung.py', base="Win32Gui"),]
except ImportError:
    from setuptools import setup
    executables = None
import sys

sys.path.append("pingpung")

exe_build_options = dict(path=sys.path,
                    include_files=["pingpung/data"],
                    icon='pingpung/data/icon.ico',
                    excludes = ["tkinter"],
                    base = 'Win32GUI')



setup(name='PingPung',
      version = '0.0.4',
      description = 'Python3/QT4 Multiplatform Ping Application',
      options = dict(build_exe = exe_build_options),
      executables = executables,
      test_suite = "tests",
)
