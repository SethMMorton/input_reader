#! /usr/bin/env python

#from ez_setup import use_setuptools
from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup

# Read the _version.py file for the module version number
import re
from os.path import join
VERSIONFILE = join('input_reader', '_version.py')
with open(VERSIONFILE, "rt") as fl:
    versionstring = fl.readline().strip()
m = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", versionstring)
if m:
    VERSION = m.group(1)
else:
    s = "Unable to locate version string in {0}"
    raise RuntimeError (s.format(VERSIONFILE))

DESCRIPTION = 'Define and read input files with an API inspired by argparse'
try:
    with open('README.rst') as fl:
        LONG_DESCRIPTION = fl.read()
except IOError:
    LONG_DESCRIPTION = DESCRIPTION

setup(name='input_reader',
      version=VERSION,
      author='Seth M. Morton',
      author_email='drtuba78@gmail.com',
      url='https://github.com/SethMMorton/input_reader',
      license='MIT',
      packages=['input_reader'],
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      use_2to3=True,
      test_suite='input_reader.tests.loadAllTests',
      classifiers=(
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities',
      )
     )
