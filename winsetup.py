import sys

from cx_Freeze import setup as cxsetup
from cx_Freeze import Executable

# So I can define most options in actual project setup.py and just import here
import setup as ppsetup

executables = [Executable('pingpung/pingpung.py', base="Win32Gui")]

exe_build_options = dict(path=sys.path,
                         include_files=["pingpung/data", "pingpung/ppui", "pingpung/VERSION", "README.md"],
                         icon='pingpung/data/icon.ico',
                         excludes=["tkinter"],
                         base='Win32GUI')

long = ppsetup.long