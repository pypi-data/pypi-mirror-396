#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="fleandr-test-package",
    version="0.2.0",
    description="Test package for PyPI cleanup utility",
    author="fleandr",
    author_email="fleandr@example.com",
    py_modules=["fleandr_test"],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

