# Copyright 2010 Paul J. Davis <paul.joseph.davis@gmail.com>
#
# This file is part of the Smithy package released under the MIT license.

import t

@t.test
def test_no_tasks():
    t.raises(t.TaskNotFoundError, t.app.run, None, ["foo"])

@t.test
def test_one_task():
    @t.task
    def foo():
        return 3
    t.app.run(None, ["foo"])
    t.eq(t.app._dbg, [("foo", 3)])

@t.test
def test_two_tasks():
    @t.task
    def foo():
        return 2
    @t.task
    def bar():
        return "hi"
    t.app.run(None, ["foo", "bar"])
    t.eq(t.app._dbg, [("foo", 2), ("bar", "hi")])

@t.test
def test_task_arg():
    @t.task
    def bizzle(task):
        from smithy.task import Task
        t.eq(isinstance(task, Task), True)
        return task.name
    t.app.run(None, ["bizzle"])
    t.eq(t.app._dbg, [("bizzle", "bizzle")])

@t.test
def test_task_run_once():
    @t.task
    def foo():
        return 2
    t.app.run(None, ["foo"])
    t.eq(t.app._dbg, [("foo", 2)])
    t.app.run(None, ["foo"])
    t.eq(t.app._dbg, [("foo", 2)])

@t.test
def test_no_decorator():
    def foo():
        return 2
    t.task("foo")(foo)
    t.app.run(None, ["foo"])
    t.eq(t.app._dbg, [("foo", 2)])

@t.test
def test_adding_more_actions():
    def foo():
        return 2
    def bar():
        return "hi"
    t.task("foo")(foo)
    t.task("foo")(bar)
    t.app.run(None, ["foo"])
    t.eq(t.app._dbg, [("foo", 2), ("foo", "hi")])
    t.raises(t.TaskNotFoundError, t.app.run, None, ["bar"])

@t.test
def test_lambda_action():
    print t.task(lambda: 4.5)
    print t.app.mgr.tasks
    t.app.run(None, ["<lambda>.1"])
    t.eq(t.app._dbg, [("<lambda>.1", 4.5)])
