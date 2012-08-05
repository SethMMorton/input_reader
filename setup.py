from distutils.core import setup
from os.path import join

setup(name='input_reader',
      version='1.0',
      author='Seth M. Morton',
      author_email='drtuba78@gmail.com',
      url='https://github.com/SethMMorton/input_reader',
      #download_url='',
      py_modules=['input_reader'],
      scripts=[join('scripts', 'natsort')],
      description='Easily read in block- and keyword-type input files',
      #long_description='',
     )
