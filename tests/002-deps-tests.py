# Copyright 2010 Paul J. Davis <paul.joseph.davis@gmail.com>
#
# This file is part of the Smithy package released under the MIT license.

import t

@t.test
def test_trigger_single_dep():
    @t.task
    def foo():
        return 2
    @t.task([foo])
    def bar():
        return "hi"
    t.app.run(None, ["bar"])
    t.eq(t.app._dbg, [("foo", 2), ("bar", "hi")])

@t.test
def test_doesnt_trigger_children():
    @t.task
    def foo():
        return 2
    @t.task(["foo"])
    def bar():
        return "hi"
    t.app.run(None, ["foo"])
    t.eq(t.app._dbg, [("foo", 2)])

@t.test
def test_not_rerun_as_dep():
    @t.task
    def foo():
        return 2
    @t.task(["foo"])
    def bar():
        return "hi"
    t.app.run(None, ["foo"])
    t.eq(t.app._dbg, [("foo", 2)])
    t.app.run(None, ["bar"])
    t.eq(t.app._dbg, [("foo", 2), ("bar", "hi")])

@t.test
def test_multi_deps():
    @t.task
    def foo():
        return 2
    @t.task
    def bar():
        return "hi"
    @t.task(["foo", bar])
    def frog():
        return "bird"
    t.app.run(None, ["frog"])
    t.eq(t.app._dbg, [
        ("foo", 2),
        ("bar", "hi"),
        ("frog", "bird")
    ])

@t.test
def test_diamond_deps():
    @t.task
    def foo():
        return 2
    @t.task([foo])
    def bar():
        return "hi"
    @t.task(["foo"])
    def frog():
        return "bird"
    @t.task([bar, frog])
    def proton():
        return False
    t.app.run(None, ["proton"])
    t.eq(t.app._dbg, [
        ("foo", 2),
        ("bar", "hi"),
        ("frog", "bird"),
        ("proton", False)
    ])

