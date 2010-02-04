
import types

from trowl.application import application
from trowl.task import Task
from trowl.filetask import FileTask, FileCreationTask
from trowl.multitask import MultiTask

__all__ = ["task", "deps", "file", "multitask", "ns"]

FUNC_TYPES = (types.FunctionType, types.BuiltinFunctionType, types.LambdaType)
METH_TYPES = (types.MethodType, types.BuiltinMethodType)
def _get_name(func):
    if isinstance(func, basestring):
        return func
    elif isinstance(func, FUNC_TYPES):
        return func.func_name
    elif isinstance(func, METH_TYPES):
        return func.im_func.func_name
    else:
        raise TypeError("Unable to make a task from type: %s" % func.__class__)

def task(*args, **kwargs):
    name = kwargs.get("name", None)
    type = kwargs.get("type", Task)
    action = kwargs.get("action", None)
    deps = kwargs.get("deps", None)
    
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        deps = args[0]
    elif len(args) == 1:
        if action is None and callable(args[0]):
            action = args[0]
        if name is None:
            name = _get_name(args[0])
    elif len(args) == 2:
        if action is None and callable(args[0]):
            action = args[0]
        if name is None:
            name = _get_name(args[0])
        if deps is None and isinstance(args[1], (list, tuple)):
            deps = map(_get_name, args[1])
    else:
        raise TaskArgumentError()

    if name is None: # Need to recurse
        return lambda f: task(f, type=type, action=action, deps=deps)
    
    application.mgr.add_task(type, name, action=action, deps=deps)
    return func

def file(fname, *args, **kwargs):
    type = FileTask if kwargs.get("recreate", True) else FileCreationTask
    task(*args, type=type, name=fname)
    def _create_task(func):
        return task(func, type=type, name=fname)
    return _create_task

def multitask(func):
    return task(func, type=MultiTask)

def rule(pattern, sources):
    def _create_rule(func):
        application.add_rule(pattern, sources, func)
        return func
    return _create_rule

class ns(object):
    def __init__(self, *args):
        self.scopes = map(str, args)
    
    def __enter__(self):
        map(application.mgr.push_scope, self.scopes)
        return self

    def __exit__(self):
        map(application.mgr.pop_scope, reversed(self.scopes))
