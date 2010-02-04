# Copyright 2009 Paul J. Davis <paul.joseph.davis@gmail.com>
#
# This file is part of the Trawl package released under the MIT license.
import os
import unittest
import uuid

from trawl.application import application as app
from trawl.decorators import *
from trawl.exceptions import *

def tmpfname():
    base = os.path.join(os.path.dirname(__file__), "data", "tmp")
    if not os.path.isdir(base):
        os.makedirs(base)
    return os.path.join(base, uuid.uuid4().hex.upper())

def test(func):
    def _f(*args, **kwargs):
        app.clear(tasks=True)
        func(*args, **kwargs)
    _f.func_name = func.func_name
    return _f

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

def is_js_object(obj):
    assert isinstance(obj, spidermonkey.Object), \
            "%r is not an instance of spdermonkey.Object." % obj
