# Copyright 2009 Paul J. Davis <paul.joseph.davis@gmail.com>
#
# This file is part of the Trawl package released under the MIT license.
import functools
import os
import unittest
import uuid

from trawl.application import application as app
from trawl.decorators import *
from trawl.exceptions import *
from trawl.filelist import FileList, FileListIter
from trawl.path import aspath, path

DATA_DIR = path(__file__).parent / "data"

FILE_PATHS = map(path, """
    CVS .svn .git .dummy x.bak x x~ core x.c xyz.c abc.c abc.h abc.x existing
""".split())

def tmpfname(name=None):
    if not DATA_DIR.isdir():
        DATA_DIR.makedirs()
    if name is None:
        name = uuid.uuid4().hex.upper()
    return DATA_DIR / name

def test(func):
    @functools.wraps(func)
    def _f(*args, **kwargs):
        # Reset the internal state before each test.
        app.clear(tasks=True)
        func(*args, **kwargs)
        if DATA_DIR.isdir():
            DATA_DIR.rmtree()
    return _f

def filetest(func):
    @functools.wraps(func)
    def _f(*args, **kwargs):
        for p in FILE_PATHS:
            p = DATA_DIR / "lists" / p
            if not p.parent.isdir():
                p.parent.makedirs()
            p.touch()
        cwd = path.getcwd()
        try:
            os.chdir(DATA_DIR/"lists")
            func(*args, **kwargs)
        finally:
            os.chdir(cwd)
        if DATA_DIR.isdir():
            DATA_DIR.rmtree()
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
        return
    func_name = getattr(func, "func_name", "<builtin_function>")
    mesg = "Function %s did not raise %s" % (func_name, exctype.__name__)
    raise AssertionError(mesg)

def isinstance(obj, type):
    func = __builtins__["isinstance"]
    assert func(obj, type), "%r is not an instance of %r." % (obj, type)
