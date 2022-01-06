#!/usr/bin/env python3

import os
import sys
from os.path import dirname
from os.path import join as pathjoin
from setuptools import find_packages
from setuptools import setup


test:str = "ok"
NAME = 'acapela_box'
VERSION = '0.1'


with open(pathjoin(dirname(__file__), 'README.md')) as f:
    DESCRIPTION = f.read()

REQUIRED, REQUIRED_URL = [], []

with open('requirements.txt') as f:
    for line in f.readlines():
        if 'http://' in line or 'https://' in line:
            REQUIRED_URL.append(line)

        else:
            REQUIRED.append(line)


packages = sorted(set(['acapela_box']))

setup(
    name=NAME,
    version=VERSION,
    description='API Online acapela voices.',
    long_description=DESCRIPTION,
    author='alekssamos',
    author_email='aleks-samos@yandex.ru',
    maintainer='alekssamos',
    maintainer_email='aleks-samos@yandex.ru',
    url='https://github.com/alekssamos/acapela-box/',
    license='GPLv3',
    packages=packages,
    install_requires=REQUIRED,
    dependency_links=REQUIRED_URL,
    include_package_data=True,
)
