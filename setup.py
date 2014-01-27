#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuphelp import current_version, PyTest, Updater, Clean
from os.path import join

DESCRIPTION = 'Define and read input files with an API inspired by argparse'
try:
    with open('README.rst') as fl:
        LONG_DESCRIPTION = fl.read()
except IOError:
    LONG_DESCRIPTION = DESCRIPTION

setup(name='input_reader',
      version=current_version(),
      author='Seth M. Morton',
      author_email='drtuba78@gmail.com',
      url='https://github.com/SethMMorton/input_reader',
      license='MIT',
      packages=find_packages(),
      package_data={'input_reader': [join('include', 'input_reader.h')]},
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      tests_require=['pytest'],
      cmdclass={'test': PyTest, 'version_update': Updater, 'distclean': Clean},
      classifiers=(
        'Development Status :: 5 - Production/Stable',
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
