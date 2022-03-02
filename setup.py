# -*- coding: utf-8 -*-

from setuptools import setup

# Avoid directly importing the module. Prevents potential circular
# references when dependency needs to be installed via setup.py, so it
# is not yet available to setup.py
exec(open("hl7/version.py").read())

setup(
    name="hl7",
    version=get_version(),  # noqa
    description="Python library parsing HL7 v2.x messages",
    long_description="""
    python-hl7 is a simple library for parsing messages of Health Level 7
    (HL7) version 2.x into Python objects.

    * Documentation: http://python-hl7.readthedocs.org
    * Source Code: http://github.com/johnpaulett/python-hl7
    """,
    author="John Paulett",
    author_email="john@paulett.org",
    url="http://python-hl7.readthedocs.org",
    project_urls={
        "Source": "https://github.com/johnpaulett/python-hl7",
    },
    license="BSD",
    platforms=["POSIX", "Windows"],
    keywords=[
        "HL7",
        "Health Level 7",
        "healthcare",
        "health care",
        "medical record",
        "mllp",
    ],
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Communications",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=["hl7", "hl7.mllp"],
    install_requires=[],
    test_suite="tests",
    tests_require=[],
    entry_points={
        "console_scripts": [
            "mllp_send=hl7.client:mllp_send",
        ],
    },
    zip_safe=True,
)
