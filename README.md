# PingPung 
## A Python3 and PyQT4 Multiplatform Desktop Ping Application

PingPung is intended to fill the niche of a truly multiplatform graphical ping application.  Unlike other desktop ping
utilities, it does NOT use your operating system's builtin 'ping' program at all.  Instead, it uses a pure Python 3
library which creates its own socket.  **Because of this, it will require root privileges on many/all platforms.**
If you're uncomfortable with that, there are many other platform-specific graphical ping apps out there which do not 
require root (because they're just wrappers around the OS's existing ping util).   
  
### A note about dependencies
This application uses PyQt4 as the graphical library, which is not installable via PyPI and will need to be done
separately.  On Debian/Ubuntu, for example, it's as simple as

    sudo apt-get install python3-pyqt4

If you intend to build for Windows, you'll also need to install cx_freeze by any method you choose, and build with
    
    python setup.py build_exe

The ping library in use was derived from a standalone application found here
http://www.falatic.com/index.php/39/pinging-with-python