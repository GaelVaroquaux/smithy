# Copyright 2010 Paul J. Davis <paul.joseph.davis@gmail.com>
#
# This file is part of the Smithy package released under the MIT license.

import t

@t.test
def test_basic_description():
    @t.task
    def foo():
        "bar"
    t.eq(t.app.mgr.lookup("foo").descr, "bar")

@t.test
def test_add_description():
    @t.task
    def foo():
        pass
    t.desc("foo", "baz!")
    t.eq(t.app.mgr.lookup("foo").descr, "baz!")

@t.test
def test_add_description_first():
    t.desc("foo", "bazinga")
    @t.task
    def foo():
        "Not used as a description"
        pass
    t.eq(t.app.mgr.lookup("foo").descr, "bazinga")

@t.test
def test_override_docstring():
    @t.task
    def foo():
        "Not the description"
        pass
    t.desc("foo", "wheeee")
    t.eq(t.app.mgr.lookup("foo").descr, "wheeee")

@t.test
def test_from_func():
    @t.task
    def foo():
        "Hi"
        pass
    t.desc(foo, "yay")
    t.eq(t.app.mgr.lookup("foo").descr, "yay")
