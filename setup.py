#!/usr/bin/env python

# This must be at the top to force cffi to use setuptools instead od distools
from setuptools import setup

import platform

import numad

name = 'numad'
path = 'numad'

## Automatically determine project version ##
try:
    from hgdistver import get_version
except ImportError:
    def get_version():
        import os
        
        d = {'__name__':name}

        # handle single file modules
        if os.path.isdir(path):
            module_path = os.path.join(path, '__init__.py')
        else:
            module_path = path
                                                
        with open(module_path) as f:
            try:
                exec(f.read(), None, d)
            except:
                pass

        return d.get("__version__", 0.1)

## Use py.test for "setup.py test" command ##
from setuptools.command.test import test as TestCommand
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)

## Try and extract a long description ##
readme = ""
for readme_name in ("README", "README.rst", "README.md",
                    "CHANGELOG", "CHANGELOG.rst", "CHANGELOG.md"):
    try:
        readme += open(readme_name).read() + "\n\n"
    except (OSError, IOError):
        continue

## Finally call setup ##
setup(
    name = name,
    version = get_version(),
    packages = [path],
    author = "Jay Coles",
    author_email = "code@pocketnix.org",
    # Setting myself as the maintainer as well so i can specify 2 email addresses
    # and let others take over maintainership of the project but still be
    # able to contact me about issues
    maintainer="Jay Coles",
    maintainer_email="jayc@anchor.net.au",
    description = "Utilities for anchor admins to speed up solving issues",
    long_description = readme,
    license = "BSD 2 clause",
    keywords = "sysadmin utility elasticsearch es search typeahead",
    download_url = "https://github.com/exec-all/numad",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        ],
    platforms=None,
    url = "https://github.com/exec-all/numad",
    entry_points = {"console_scripts":["numad=numad:main",],
                   },
#    scripts = ['scripts/dosomthing'],
    zip_safe = True,
    setup_requires = [],
    install_requires = ["blessed>=1.9.5", 'aioes'],
    tests_require = ['tox', 'pytest', 'pytest-cov', 'pytest-mock', 'mock'],
    cmdclass = {'test': PyTest},
)
