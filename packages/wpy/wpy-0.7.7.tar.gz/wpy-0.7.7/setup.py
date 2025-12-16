#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

from wpy import __version__
from setuptools import setup, find_packages

setup(
    name = 'wpy',
    version = __version__,
    keywords='python3',
    description = 'a library for python Developer',
    license = 'MIT License',
    url = 'https://github.com/wxnacy/wpy',
    author = 'wxnacy',
    author_email = 'wxnacy@gmail.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = [
        'requests>=2.19.1',
        'pycrypto>=2.6.1',
        'Pillow>=5.2.0',
        'click>=6.7',
        'xmltodict',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': ['wpy=wpy.app:run']
        },
    #  scripts=['bin/wpytool']
)

