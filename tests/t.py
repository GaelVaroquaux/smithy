# This file is part of the Belt package released under the MIT license.
# See the NOTICE for more information.

import inspect
import os
import re
import unittest

import belt

dirname = os.path.dirname(__file__)
base = belt.path(dirname) / "tmp"

class root(object):
    def __init__(self, path):
        self.path = belt.path(path)
    def __call__(self, func):
        def f(*args, **kwargs):
            if self.path.exists():
                self.path.rmtree()
            func(self.path)
        f.func_name = func.func_name
        return f

def eq(a, b):
    assert a == b, "%r != %r" % (a, b)

def ne(a, b):
    assert a != b, "%r == %r" % (a, b)

def lt(a, b):
    assert a < b, "%r >= %r" % (a, b)

def gt(a, b):
    assert a > b, "%r <= %r" % (a, b)

def isin(a, b):
    assert a in b, "%r is not in %r" % (a, b)

def isnotin(a, b):
    assert a not in b, "%r is in %r" % (a, b)

def has(a, b):
    assert hasattr(a, b), "%r has no attribute %r" % (a, b)

def hasnot(a, b):
    assert not hasattr(a, b), "%r has an attribute %r" % (a, b)

def raises(exctype, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except exctype, inst:
        pass
    else:
        func_name = getattr(func, "func_name", "<builtin_function>")
        raise AssertionError("Function %s did not raise %s" % (
            func_name, exctype.__name__))

