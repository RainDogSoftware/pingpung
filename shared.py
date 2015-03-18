# Making these as attributes so they can be imported by both setups

name = 'PingPung'
long = "PingPung is intended to fill the niche of a truly multiplatform graphical ping application.  Unlike other desktop ping utilities, it does NOT use your operating system's builtin 'ping' program at all.  Instead, it uses a pure Python 3 library which creates its own socket.  **Because of this, it will require root privileges on many platforms.** If you're uncomfortable with that, there are many other platform-specific graphical ping apps out there which do not require root (because they're just wrappers around the OS's existing ping util)."
version="0.1.9"
author="Josh Price"
author_email="Price.JoshuaD@Gmail.com"
description='Python3/QT4 Multiplatform Ping Application'
pplicense="GPLv2"
url = 'https://github.com/RainDogSoftware/pingpung/'
download_url = 'https://github.com/RainDogSoftware/pingpung/tarball/0.1.9'
keywords="ping networking network testing"
packages=["pingpung",
          "pingpung.pplib"]
classifiers=[
      "Development Status :: 3 - Alpha",
      "Topic :: Utilities",
      "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
      "Operating System :: OS Independent",
      "Programming Language :: Python :: 3",
      "Topic :: Internet",
      "Topic :: System :: Networking :: Monitoring",
      "Topic :: Utilities",
      ]