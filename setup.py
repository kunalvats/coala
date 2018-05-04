#!/usr/bin/env python3

import datetime
import locale
import platform
import sys
from os import getenv
from subprocess import call

import setuptools.command.build_py
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

from coalib import assert_supported_version, get_version
from coalib.misc.BuildManPage import BuildManPage

try:
    lc = locale.getlocale()
    pf = platform.system()
    if pf != 'Windows' and lc == (None, None):
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
except (ValueError, UnicodeError):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

VERSION = '0.12.0.dev99999999999999'

assert_supported_version()


class BuildPyCommand(setuptools.command.build_py.build_py):

    def run(self):
        if platform.system() != 'Windows':
            self.run_command('build_manpage')
        setuptools.command.build_py.build_py.run(self)


class PyTestCommand(TestCommand):
    """
    From https://pytest.org/latest/goodpractices.html
    """
    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.test')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


class BuildDocsCommand(setuptools.command.build_py.build_py):
    apidoc_command = (
        'sphinx-apidoc', '-f', '-o', 'docs',
        '--no-toc',
        'coalib'
    )
    make_command = ('make', '-C', 'docs', 'html', 'SPHINXOPTS=-W')

    def run(self):
        err_no = call(self.apidoc_command)
        if not err_no:
            err_no = call(self.make_command)
        sys.exit(err_no)


# Generate API documentation only if we are running on readthedocs.io
on_rtd = getenv('READTHEDOCS', None) is not None
if on_rtd:
    call(BuildDocsCommand.apidoc_command)
    if 'dev' in '0.12.0.dev99999999999999':
        current_version = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        call(['python3', '.misc/adjust_version_number.py', 'coalib/VERSION',
              '-b {}'.format(current_version)])
        VERSION = get_version()


with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()

with open('test-requirements.txt') as requirements:
    test_required = requirements.read().splitlines()

with open('README.rst') as readme:
    long_description = readme.read()

extras_require = None
data_files = None
if __name__ == '__main__':
    if platform.system() != 'Windows':
        data_files = [('man/man1', ['coala.1'])]
    else:
        data_files = None

if __name__ == '__main__':
    setup(name='coala',
          version=VERSION,
          description='Linting and Fixing Code for All Languages',
          author='The coala developers',
          author_email='coala.analyzer@gmail.com',
          maintainer='Lasse Schuirmann, Fabian Neuschmidt, Mischa Kr\xfcger'
                     if not on_rtd else 'L.S., F.N., M.K.',
          maintainer_email=('lasse.schuirmann@gmail.com, '
                            'fabian@neuschmidt.de, '
                            'makman@alice.de'),
          url='http://coala.io/',
          platforms='any',
          packages=find_packages(exclude=('build.*', 'tests', 'tests.*')),
          install_requires=required,
          extras_require=extras_require,
          tests_require=test_required,
          package_data={'coalib': ['system_coafile', 'VERSION',
                                   'bearlib/languages/documentation/*.coalang']
                        },
          license='AGPL-3.0',
          data_files=data_files,
          long_description=long_description,
          entry_points={
              'console_scripts': [
                  'coala = coalib.coala:main',
                  'coala-ci = coalib.coala_ci:main',
                  'coala-json = coalib.coala_json:main',
                  'coala-format = coalib.coala_format:main',
                  'coala-delete-orig = coalib.coala_delete_orig:main',
              ],
          },
          # from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          classifiers=[
              'Development Status :: 4 - Beta',

              'Environment :: Console',
              'Environment :: MacOS X',
              'Environment :: Win32 (MS Windows)',
              'Environment :: X11 Applications :: Gnome',

              'Intended Audience :: Science/Research',
              'Intended Audience :: Developers',

              'License :: OSI Approved :: GNU Affero General Public License '
              'v3 or later (AGPLv3+)',

              'Operating System :: OS Independent',

              'Programming Language :: Python :: Implementation :: CPython',
              'Programming Language :: Python :: 3.4',
              'Programming Language :: Python :: 3.5',
              'Programming Language :: Python :: 3 :: Only',

              'Topic :: Scientific/Engineering :: Information Analysis',
              'Topic :: Software Development :: Quality Assurance',
              'Topic :: Text Processing :: Linguistic'],
          cmdclass={'docs': BuildDocsCommand,
                    'build_manpage': BuildManPage,
                    'build_py': BuildPyCommand,
                    'test': PyTestCommand})
