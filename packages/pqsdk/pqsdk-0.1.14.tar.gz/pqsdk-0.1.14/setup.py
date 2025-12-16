# !/usr/bin/env python
# -*- coding=utf-8 -*-,
import os
from setuptools import setup, find_packages

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


def get_version():
    scope = {}
    version = '0.0.1'
    version_file = os.path.join(THIS_FOLDER, "pqsdk", "version.py")
    if os.path.exists(version_file):
        with open(version_file) as fp:
            exec(fp.read(), scope)
        version = scope.get('__version__', '0.0.1')
    return version


def get_long_description():
    with open(os.path.join(THIS_FOLDER, 'README.md'), 'rb') as f:
        long_description = f.read().decode('utf-8')
    return long_description


def get_install_requires():
    requirement_file = os.path.join(THIS_FOLDER, "requirements.txt")
    if not os.path.isfile(requirement_file):
        return []
    with open(requirement_file) as f:
        requirements = [line.strip() for line in f if line.strip()]
    return requirements


setup(
    name='pqsdk',
    version=get_version(),
    description="SDK for stock analysis and strategy backtest.",
    packages=find_packages(exclude=("tests",)),
    author="PinkQuant",
    author_email="pinkquant@163.com",
    maintainer="topbip",
    maintainer_email="pinkquant@163.com",
    url="https://www.pinkquant.com",
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    install_requires=get_install_requires(),
    platforms=["all"],
    entry_points={
        'console_scripts': [
            'pqsdk=pqsdk.__main__:main',
        ],
    },
)
