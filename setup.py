#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

import hl7 as _hl7
    
setup(
    name = 'hl7',
    version = _hl7.__version__,
    description = 'Python library parsing HL7 v2.x messages',
    long_description = _hl7.__doc__,
    author = _hl7.__author__,
    author_email = _hl7.__email__,
    url = _hl7.__url__,
    license = _hl7.__license__,
    platforms = ['POSIX', 'Windows'],
    keywords = ['HL7', 'Health Level 7', 'healthcare', 'health care', 'medical record'],
    classifiers = [
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Topic :: Communications',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = ['hl7'],
    test_suite = 'tests',
    tests_require = ['mock'],
    entry_points = {
        'console_scripts': [
            'mllp_send = hl7.client:mllp_send',
        ],
    },
    zip_safe=True,
)
