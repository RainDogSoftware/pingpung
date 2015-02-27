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


exe_build_options = dict(path=sys.path,
                         include_files=["pingpung/data", "pingpung/ppui", "pingpung/VERSION", "README.md"],
                         icon='pingpung/data/icon.ico',
                         excludes=["tkinter"],
                         base='Win32GUI')

long = "PingPung is intended to fill the niche of a truly multiplatform graphical ping application.  Unlike other desktop ping utilities, it does NOT use your operating system's builtin 'ping' program at all.  Instead, it uses a pure Python 3 library which creates its own socket.  **Because of this, it will require root privileges on many platforms.** If you're uncomfortable with that, there are many other platform-specific graphical ping apps out there which do not require root (because they're just wrappers around the OS's existing ping util)."

setup(name='PingPung',
      version="0.1.5",
      author="Josh Price",
      author_email="Price.JoshuaD@Gmail.com",
      description='Python3/QT4 Multiplatform Ping Application',
      license="GPLv2",
      url = 'https://github.com/RainDogSoftware/pingpung/',
      download_url = 'https://github.com/RainDogSoftware/pingpung/tarball/0.1.5',
      keywords="ping networking network testing",
      packages=["pingpung",
                "pingpung.pplib"],
      options=dict(build_exe=exe_build_options,
                   ),
      long_description=long,
      executables=executables,
      entry_points={'gui_scripts': ['pingpung = pingpung']},
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
