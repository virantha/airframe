#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
requirements = open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='airframe',
    version='0.1.0',
    description='Push images to a Toshiba FlashAir Wifi SD card',
    long_description=readme + '\n\n' + history,
    author='Virantha Ekanayake',
    author_email='virantha@gmail.com',
    url='https://github.com/virantha/airframe',
    packages=[
        'airframe',
    ],
    package_dir={'airframe': 'airframe'},
    include_package_data=True,
    install_requires=required,
    license="ASL2",
    zip_safe=False,
    keywords='airframe',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved ::  ASL License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)
