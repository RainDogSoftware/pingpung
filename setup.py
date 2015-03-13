import sys
import os

from setuptools import setup

sys.path.append("pingpung")
sys.path.append("pingpung/data")

long = "PingPung is intended to fill the niche of a truly multiplatform graphical ping application.  Unlike other desktop ping utilities, it does NOT use your operating system's builtin 'ping' program at all.  Instead, it uses a pure Python 3 library which creates its own socket.  **Because of this, it will require root privileges on many platforms.** If you're uncomfortable with that, there are many other platform-specific graphical ping apps out there which do not require root (because they're just wrappers around the OS's existing ping util)."

setup(name='PingPung',
      version="0.1.9",
      author="Josh Price",
      author_email="Price.JoshuaD@Gmail.com",
      description='Python3/QT4 Multiplatform Ping Application',
      license="GPLv2",
      url = 'https://github.com/RainDogSoftware/pingpung/',
      download_url = 'https://github.com/RainDogSoftware/pingpung/tarball/0.1.9',
      keywords="ping networking network testing",
      packages=["pingpung",
                "pingpung.pplib"],
      long_description=long,
      entry_points={'console_scripts': ['pingpung = pingpung.pingpung:launch']},
      include_package_data = True,
      package_data = {
        '': ['VERSION'],
        '': ['ppui/*'],
        'ppui': ['*'],
      },
      classifiers=[
      "Development Status :: 3 - Alpha",
      "Topic :: Utilities",
      "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
      "Operating System :: OS Independent",
      "Programming Language :: Python :: 3",
      "Topic :: Internet",
      "Topic :: System :: Networking :: Monitoring",
      "Topic :: Utilities",
      ],
      test_suite="tests",
     )
