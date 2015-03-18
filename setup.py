import sys
import os
import shared

from setuptools import setup

sys.path.append("pingpung")
sys.path.append("pingpung/data")



setup(name=shared.name,
      version=shared.version,
      author=shared.author,
      author_email=shared.author_email,
      description=shared.description,
      license=shared.pplicense,
      url=shared.url,
      download_url=shared.download_url,
      keywords=shared.keywords,
      packages=shared.packages,
      long_description=shared.long,
      entry_points={'console_scripts': ['pingpung = pingpung.pingpung:launch']},
      include_package_data = True,
      package_data = {
        '': ['VERSION'],
        '': ['ppui/*'],
        'ppui': ['*'],
      },
      classifiers=shared.classifiers,
      test_suite="tests",
     )
