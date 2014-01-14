#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
import sys


from setuptools import setup, find_packages

import airframe
from airframe.version import __version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.rst', 'HISTORY.rst', 'TODO.rst')

packages = find_packages(exclude="tests")

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='airframe',
    version=__version__,
    description='Push images to a Toshiba FlashAir Wifi SD card',
    long_description=long_description,
    author='Virantha N. Ekanayake',
    author_email='virantha@gmail.com',
    url='https://github.com/virantha/airframe',
    packages=packages,
    include_package_data=True,
    install_requires=required,
    license="ASL2",
    zip_safe=True,
    keywords='airframe',
    entry_points = {
            'console_scripts': [
                    'airframe = airframe.airframe:main'
                ],
        },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
)
