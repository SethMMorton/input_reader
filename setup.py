#! /usr/bin/env python

# In case setuptools is not installed
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

# Read the _version.py file for the module version number
import re
from os.path import join
VERSIONFILE = join('input_reader', '_version.py')
with open(VERSIONFILE, "rt") as fl:
    versionstring = fl.readline().strip()
m = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", versionstring)
if m:
    version = m.group(1)
else:
    s = "Unable to locate version string in {0}"
    raise RuntimeError (s.format(VERSIONFILE))

setup(name='input_reader',
      version=version,
      author='Seth M. Morton',
      author_email='drtuba78@gmail.com',
      url='https://github.com/SethMMorton/input_reader',
      #download_url='',
      packages=['input_reader'],
      description='An easy interface for reading block- and keyword-type input files',
      #long_description='',
     )
