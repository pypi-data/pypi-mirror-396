#!/usr/bin/env python
"""This module contains setup instructions for ytextract."""
import codecs
import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

__version__ = "0.0.1"

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

setup(
    name="ytextract",
    version=__version__,
    author="Josh-XT",
    packages=["ytextract"],
    package_data={
        "": ["LICENSE"],
    },
    url="https://github.com/Josh-XT/ytextract",
    license="The Unlicense (Unlicense)",
    entry_points={
        "console_scripts": ["ytextract = ytextract.cli:main"],
    },
    install_requires=[
        "selenium",
        "webdriver-manager",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
    description=("Python 3 library for downloading YouTube Videos."),
    include_package_data=True,
    long_description_content_type="text/markdown",
    long_description=long_description,
    zip_safe=True,
    python_requires=">=3.7",
    project_urls={"Bug Reports": "https://github.com/Josh-XT/ytextract/issues"},
    keywords=[
        "youtube",
        "download",
        "video",
        "stream",
    ],
)
