# This file is part of Belt released under the MIT license. 
# See the NOTICE for more information.

import os
from setuptools import setup, find_packages

README = os.path.join(os.path.dirname(__file__), 'README.rst')

setup(
    name = 'belt',
    version = '0.1',

    description = 'Framework for executing software pipelines.',
    long_description = open(README).read(),
    author = 'Paul J. Davis',
    author_email = 'paul.joseph.davis@gmail.com',
    license = 'MIT',
    url = 'http://github.com/davisp/belt',

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries',
    ],
    
    packages = find_packages(),
    include_package_data = True,
    scripts = ['bin/belt'],
    
    test_suite = 'nose.collector',
)

