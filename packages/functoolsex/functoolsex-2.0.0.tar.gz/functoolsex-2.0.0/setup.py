#!/usr/bin/env python

from os.path import exists
from setuptools import setup

setup(name='functoolsex',
      version='2.0.0',
      description='ex(fn, pytoolz, ...) and faster on CPython and PyPy',
      url='https://github.com/aymazon/functools-ex',
      author='Tony L. Fan',
      author_email='aymazon@gmail.com',
      license='MIT',
      keywords='fn pytoolz functional utility itertools functools',
      packages=['functoolsex'],
      package_data={'functoolsex': ['tests/*.py']},
      long_description=(open('README.rst').read() if exists('README.rst') else ''),
      install_requires=(open('requirements.txt').readlines() if exists('requirements.txt') else []),
      zip_safe=False,
      classifiers=[
          "Development Status :: 5 - Production/Stable", "License :: OSI Approved :: MIT License",
          "Programming Language :: Python", "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5", "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7", "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9", "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11", "Programming Language :: Python :: 3.12",
          "Programming Language :: Python :: 3.13", "Programming Language :: Python :: 3.14",
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy"
      ])
