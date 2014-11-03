"""
Lemon
=====

Single Page Application extension for Flask.

"""

import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main('-x tests/ --cov lemon --cov-report term-missing --pdb')
        sys.exit(errno)


setup(
    name='Lemon',
    version='0.0.1',
    url='http://github.com/theorchard/lemon-py/',
    license='MIT',
    author='Michael Ortali',
    author_email='mortali@theorchard.com',
    description='Single Page Application extension for Flask',
    long_description=__doc__,
    packages=['lemon',],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'requests'],
    tests_require=[
        'pytest-cov'],
    cmdclass = {
        'test': PyTest})
