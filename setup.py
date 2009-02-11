#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 John Paulett (john -at- 7oars.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

import hl7 as _hl7

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
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
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Topic :: Communications',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    py_modules = ['hl7'],
    test_suite = 'nose.collector',
    zip_safe=True,
)
