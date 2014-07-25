from cx_Freeze import setup, Executable
import sys
#from setuptools import find_packages
# Dependencies are automatically detected, but it might need
# fine tuning.

sys.path.append("pingpung")
sys.path.append("pingpung/data")
buildOptions = dict(path=sys.path,
                    #includes=['pingpung', 'pplib'],
                    include_files=['pingpung/data/icon.ico'],
                    icon='pingpung/data/icon.ico',
                    excludes = ["tkinter"], )


base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('pingpung/pingpung.py', base=base)
]

setup(name='PingPung',
      version = '0.0.3',
      description = 'Python3/QT4 Multiplatform Ping Application',
      options = dict(build_exe = buildOptions),
      executables = executables)
