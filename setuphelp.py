'''Class to update the version in this package and update the changelog'''
from __future__ import print_function
from setuptools.command.test import test as TestCommand
from setuptools import Command
from pkg_resources import parse_version
from subprocess import call
from datetime import datetime
from glob import glob
from shutil import rmtree
from fnmatch import filter as ffilter
import re
import os
import sys

def current_version():
    # Read the _version.py file for the module version number
    VERSIONFILE = os.path.join('input_reader', '_version.py')
    with open(VERSIONFILE, "rt") as fl:
        versionstring = fl.readline().strip()
    m = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", versionstring)
    if m:
        return m.group(1)
    else:
        s = "Unable to locate version string in {0}"
        raise RuntimeError (s.format(VERSIONFILE))


# Define how to use pytest to test the code
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        sys.exit(self.run_pytest())
        #errno = self.run_pytest()
        #if errno:
        #    sys.exit(errno)
        #else:
        #    sys.exit(self.run_doctests())
    def run_pytest(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        return pytest.main(self.test_args)
    def run_doctests(self):
        # Recall current directory
        original_dir = os.path.abspath(os.curdir)
        # Go to docs directory
        os.chdir('docs')
        # Get makefile name
        if sys.platform == 'win32':
            make = 'make.bat'
        else:
            make = 'make'
        # Call the make process
        errno = call([make, 'doctest'])
        os.chdir(original_dir)
        return errno


# Clean the directory
class Clean(Command):
    description = "custom clean command that fully cleans directory tree"
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        
        # Excess files to be removed
        files = []
        dirs = glob("*.egg-info") + ['build', 'dist']
        for root, dirnames, filenames in os.walk('.'):
            for filename in ffilter(filenames, '*.py[co]'):
                files.append(os.path.join(root, filename))
            for dirname in ffilter(dirnames, '__pycache__')+ffilter(dirnames, 'xml'):
                dirs.append(os.path.join(root, dirname))
        
        for f in files:
            try:
                os.remove(f)
            except OSError:
                pass
        
        for d in dirs:
            try:
                rmtree(d)
            except OSError:
                pass
        
        # Clean the docs
        cwd = os.getcwd()
        os.chdir('docs')
        if sys.platform == 'win32':
            make = 'make.bat'
        else:
            make = 'make'
        call([make, 'clean'])
        os.chdir(cwd)


# Class to update the version
class Updater(Command):
    description = "custom command that guides you through updating to the next version"
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        # Get the current version number
        curver = current_version()
        print('The current version number is {0}'.format(curver))
        newver = raw_input('What do you want the new version to be? ')
        # Make sure the proposed version is greater than the old
        if parse_version(curver) > parse_version(newver):
            sys.exit('The new version must be greater than the current version.')
        # Get the changelog comments
        print('Please provide the changelog comments you wish to provide')
        print('Type "<eof>" when you are finished entering comments')
        log = []
        line = ''
        while line != "<eof>":
            line = raw_input(' - ')
            log.append('    - '+line)
        log[-1] = '' # Change <eof> to ''

        # Get today's date
        t = datetime.now()
        t = t.strftime('%m-%d-%Y')
        # Create the title 
        title = '{0} v. {1}'.format(t, newver)
        # Add this title to the log
        log = [title, "'"*len(title), '']+log
        
        # Read in the changelog in the docs
        changelogfile = os.path.join('docs', 'source', 'changelog.rst')
        with open(changelogfile) as clf:
            changelog = [x.rstrip() for x in clf]

        # Now read in the readme
        with open('README.rst') as rme:
            readme = [x.rstrip() for x in rme]
        
        # Change the changelog to add the new change
        changelog = changelog[:3] + log + changelog[3:]

        # Change the README to do the same
        n = readme.index('History') + 3
        readme = readme[:n] + log + readme[n:]

        # Write the new version to the _version file
        with open(os.path.join('input_reader', '_version.py'), 'w') as v:
            print("__version__ = '{0}'".format(newver), file=v)

        # Write back the changelog, README and conf
        with open(changelogfile, 'w') as clf:
            for line in changelog:
                print(line, file=clf)
        with open('README.rst', 'w') as rme:
            for line in readme:
                print(line, file=rme)
