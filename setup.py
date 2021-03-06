from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys
import re


class PyTest(TestCommand):

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def strip_rst_links(readme):
    readme = re.sub(r"`([A-Za-z\s_0-9\-]+)\s?[A-Za-z0-9_/:\.<>\-]*`_",r"\1",readme)
    return re.sub(r"\.\.\s_[a-zA-Z0-9\-_/:\.\s]+\n","",readme)


with open('README.rst') as f:
    readme = f.read()
with open('RELEASES.rst') as f:
    releases = f.read()


setup(
    name='emily',
    version='1.0.8',
    url='https://github.com/ngmcfarland/emily',
    license='Apache Software License',
    author='Nathan McFarland',
    tests_require=['pytest'],
    install_requires=['python-Levenshtein>=0.12.0',
        'fuzzywuzzy>=0.15.0',
        'Flask>=0.12',
        'Flask-Cors>=3.0.2',
        'PyYAML>=3.11',
        'six>=1.10.0',
        ],
    cmdclass={'test': PyTest},
    author_email='ngmcfarland@gmail.com',
    description='A highly customizable chatbot implemented in Python.',
    long_description=strip_rst_links(readme) + '\n\n' + releases,
    packages=['emily','emily.emily_modules'],
    package_dir={'emily':'emily'},
    include_package_data=True,
    platforms='any',
    download_url='https://github.com/ngmcfarland/emily/archive/1.0.8.tar.gz',
    entry_points={
        'console_scripts': ['emily=emily:chat','emily_server=emily:emily_server']
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    extras_require={
        'testing':['pytest'],
        'aws':['boto3>=1.4.4'],
    }
)