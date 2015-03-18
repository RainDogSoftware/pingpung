import sys
import shared

from cx_Freeze import setup
from cx_Freeze import Executable

executables = [Executable('pingpung/pingpung.py', base="Win32Gui")]

exe_build_options = dict(path=sys.path,
                         include_files=["pingpung/data", "pingpung/ppui", "pingpung/VERSION", "README.md"],
                         icon='pingpung/data/icon.ico',
                         excludes=["tkinter"],
                         base='Win32GUI',
                         )

setup(
    name=shared.name,
    long_description=shared.long,
    version=shared.version,
    author=shared.author,
    author_email=shared.author_email,
    description=shared.description,
    license=shared.pplicense,
    url=shared.url,
    download_url=shared.download_url,
    keywords=shared.keywords,
    packages=shared.packages,
    classifiers=shared.classifiers,

    executables=executables,
    options={"build_exe":exe_build_options},
)