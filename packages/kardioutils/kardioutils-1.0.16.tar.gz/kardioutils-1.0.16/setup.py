# setup.py
from setuptools import setup
from dl2050utils.__config__ import (
    name,
    package,
    description,
    author,
    author_email,
    keywords,
    get_camel,
)
from dl2050utils.__version__ import version

version_camel = get_camel(version)

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Build Tools",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

setup(
    name=name,
    version=version,
    packages=[package],
    license="MIT",
    description=description,
    author=author,
    author_email=author_email,
    keywords=keywords,
    classifiers=classifiers,
)
