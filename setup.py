import sys
import os
# having a little trouble here.  On windows, I need to use cx_freeze's "setup", but everywhere else, I just
# want standard setuptools.  The problem is that apparently cx_freeze's setup doesn't understand "test_suite"
# so I can't run unit tests.

try:
    from cx_Freeze import setup, Executable
    executables = [Executable('pingpung/pingpung.py', base="Win32Gui")]
except ImportError:
    from setuptools import setup
    executables = None

# This is an ugly hack which allows me to use setuptools' setup method instead of cx_freeze when TESTING on Windows
if sys.platform == "win32" and sys.argv[1] == "test":
    from setuptools import setup

sys.path.append("pingpung")
sys.path.append("pingpung/data")


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

exe_build_options = dict(path=sys.path,
                         include_files=["pingpung/data", "pingpung/ppui"],
                         icon='pingpung/data/icon.ico',
                         excludes=["tkinter"],
                         base='Win32GUI')

setup(name='PingPung',
      version=read('pingpung/VERSION'),
      author="Josh Price",
      author_email="Price.JoshuaD@Gmail.com",
      description='Python3/QT4 Multiplatform Ping Application',
      license="GPLv2",
      url = 'https://github.com/RainDogSoftware/pingpung/',
      download_url = 'https://github.com/RainDogSoftware/pingpung/tarball/0.1.0',
      keywords="ping networking network testing",
      packages=["pingpung",
                "pingpung.pplib"],
      options=dict(build_exe=exe_build_options,
                   ),
      long_description=read('README.md'),
      executables=executables,
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
      test_suite="tests",
     )
