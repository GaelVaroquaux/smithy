Belt - Tools for sotware pipelines
==================================

Tasks
  - Have dependencies
    * Syntax?
  - Adding actions
    * Named?
  - Arguments
    * From signature

@task
def mytask(t):
    print "First task!"

@task(["othertask", "secondtask"])
def secondtask(t):
    print "Run this after my task."

task(secondtask, ["foo", "bar"])

@task
def third(t):
    print "Decorated to be runnable."

@file("foo/bar.py", [third])
def make_bar(t):
    print "Should create a file: %s" % t.target

@multitask(["third", "secondtask", "mytask"])
def inparallel(t):
    print "Hello there govenor!"

with ns("foo", "baz", "bing"): # or, with ns("foo"), ns("baz"), ns("bing")
  
  @task
  def bar(t):
      print "This is task: %s" % t.name # "foo:bar"

# Implementation

def task(func=None, type=None, name=None):
    if not func:
        def _create_task(func):
            return task(func, type=type, name=name)
        return _create_task

    type = type or Task
    name = name or get_name(func)
    prereqs = getattr(func, "__prereqs__", [])
    func.__task__ = register_task(type, name, func, prereqs)
    return func

def file(fname, recreate=True):
    type = FileTask if recreate else FileCreationTask
    def _create_task(func):
        return task(func, type=type, name=fname)
    return _create_task

def multitask(func):
    return task(func, type=MultiTask)

def deps(*args):
    prereqs = [lookup_task(a) for a in args]
    def _add_deps(func):
        if hasattr(func.__task__):
            func.__task__.add_prereqs(prereqs)
        else:
            func.__prereqs__ = prereqs
        return func

class Namespace(object):
    def __init__(self, *args):
        self.scope = map(str, args)
    
    def __enter__(self):
        push_scope(self.scope)
    
    def __exit__(self):
        pop_scope()

ns = Namespace