try:
    from cx_Freeze import setup, Executable
    executables = [Executable('pingpung/pingpung.py', base="Win32Gui")]
except ImportError:
    from setuptools import setup
    executables = None
import sys
import os

sys.path.append("pingpung")


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

exe_build_options = dict(path=sys.path,
                         include_files=["pingpung/data", "pingpung/ppui"],
                         icon='pingpung/data/icon.ico',
                         excludes=["tkinter"],
                         base='Win32GUI')

setup(name='PingPung',
      version='0.0.4',
      author="Josh Price",
      author_email="Price.JoshuaD@Gmail.com",
      description='Python3/QT4 Multiplatform Ping Application',
      license="GPLv2",
      keywords="ping networking network testing",
      packages=["pingpung"],
      options=dict(build_exe=exe_build_options),
      executables=executables,
      long_description=read('README.md'),
      classifiers=[
      "Development Status :: 3 - Alpha",
      "Topic :: Utilities",
      "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
      "Operating System :: OS Independent",
      "Programming Language :: Python :: 3.4",
      "Topic :: Internet",
      "Topic :: System :: Networking :: Monitoring",
      "Topic :: Utilities",
      ],
      #test_suite = "tests",
     )
