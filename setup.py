from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys

import emily


class PyTest(TestCommand):
    # user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='emily',
    version=emily.__version__,
    url='https://github.com/ngmcfarland',
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
    long_description='?', # ?
    packages=['emily','emily.emily_modules'],
    package_dir={'emily':'emily'},
    include_package_data=True,
    platforms='any',
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
        'testing':['pytest'], # ?
    }
)