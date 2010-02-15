# Copyright 2010 Paul J. Davis <paul.joseph.davis@gmail.com>
#
# This file is part of the Smithy package released under the MIT license.

import t

@t.test
def test_simple_cycle():
    @t.task(["foo"])
    def foo():
        return 2
    t.raises(t.DependencyCycleError, t.app.run, None, ["foo"])

@t.test
def test_two_task_cycle():
    t.task("foo", ["bar"])(lambda: 2)
    t.task("bar", ["foo"])(lambda: "hi")
    
    for task in ["foo", "bar"]:
        t.app.clear()
        t.raises(t.DependencyCycleError, t.app.run, None, [task])
        t.eq(t.app._dbg, [])
    
@t.test
def test_ring_cycle():
    t.task("foo")(lambda: 2)
    t.task("bar")(lambda: "hi")
    t.task("frog")(lambda: "bird")
    
    t.task("foo", ["frog"])
    t.task("bar", ["foo"])
    t.task("frog", ["bar"])

    for task in ["foo", "bar", "frog"]:
        t.app.clear()
        t.raises(t.DependencyCycleError, t.app.run, None, [task])
        t.eq(t.app._dbg, [])