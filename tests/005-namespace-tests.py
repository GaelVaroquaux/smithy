# Copyright 2010 Paul J. Davis <paul.joseph.davis@gmail.com>
#
# This file is part of the Smithy package released under the MIT license.

import t

@t.test
def test_simple_ns():
    with t.ns("rho"):
        @t.task
        def foo():
            return 2
    t.raises(t.TaskNotFoundError, t.app.run, None, ["foo"])
    t.app.run(None, ["rho:foo"])
    t.eq(t.app._dbg, [("rho:foo", 2)])

def check_ns():
    t.raises(t.TaskNotFoundError, t.app.run, None, ["foo"])
    t.raises(t.TaskNotFoundError, t.app.run, None, ["rho:foo"])
    t.app.run(None, ["rho:wade:foo"])
    t.eq(t.app._dbg, [("rho:wade:foo", 2)])

@t.test
def test_nested_ns():
    with t.ns("rho"):
        with t.ns("wade"):
            @t.task
            def foo():
                return 2
    check_ns()

@t.test
def test_nested_ns_one_with():
    with t.ns("rho", "wade"):
        @t.task
        def foo():
            return 2 
    check_ns()

@t.test
def test_nested_reference():
    with t.ns("rho"):
        @t.task
        def foo():
            return 2
        with t.ns("wade"):
            @t.task([foo])
            def bar():
                return "hi"
    t.app.run(None, ["rho:wade:bar"])
    