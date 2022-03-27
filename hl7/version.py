# -*- coding: utf-8 -*-

"""
Primary version number source.

Forth element can be 'dev' < 'a' < 'b' < 'rc' < 'final'. An empty 4th
element is equivalent to 'final'.
"""
VERSION = (0, 4, 3, "final")


def get_version():
    """Provide version number

    Use verlib format [1]_:
      N.N[.N]+[{a|b|c|rc}N[.N]+][.postN][.devN]

    .. [1] http://www.python.org/dev/peps/pep-0386/
    """
    main_version = "%s.%s.%s" % VERSION[0:3]

    if len(VERSION) < 4:
        return main_version

    version_type = VERSION[3]
    if not version_type or version_type == "final":
        return main_version
    elif version_type == "dev":
        return "%s.dev" % main_version
    else:
        return "%s%s" % (main_version, version_type)
