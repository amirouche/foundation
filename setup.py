#!/usr/bin/env python
import os
from setuptools import setup
from setuptools import find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="python-copernic",
    version="0.0.0",
    author="Amirouche Boubekki",
    author_email="amirouche@hyper.dev",
    url="https://github.com/amirouche/copernic",
    description="Awesome Data Distribution.",
    long_description=read("README.md"),
    long_description_content_type='text/markdown',
    py_modules = ['copernic'],
    zip_safe=False,
    license="AGPLv3+",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
