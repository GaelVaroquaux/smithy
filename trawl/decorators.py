
import types

from trawl.application import application
from trawl.task import Task
from trawl.filetask import FileTask, FileCreationTask
from trawl.multitask import MultiTask

__all__ = ["rule", "task", "build", "multitask", "ns"]

FUNC_TYPES = (types.FunctionType, types.BuiltinFunctionType)
METH_TYPES = (types.MethodType, types.BuiltinMethodType)
LAMBDA_COUNT = 0
def _get_name(func):
    global LAMBDA_COUNT
    if isinstance(func, basestring):
        return func
    elif isinstance(func, METH_TYPES):
        return func.im_func.func_name
    elif isinstance(func, FUNC_TYPES):
        if func.func_name == "<lambda>":
            LAMBDA_COUNT += 1
            return "<lambda>.%d" % LAMBDA_COUNT
        return func.func_name
    else:
        raise TypeError("Unable to make a task from type: %s" % func.__class__)

def rule(pattern, sources):
    def _create_rule(func):
        application.mgr.add_rule(pattern, sources, func)
        return func
    return _create_rule

def task(*args, **kwargs):
    name = kwargs.get("name", None)
    type = kwargs.get("type", Task)
    action = kwargs.get("action", None)
    deps = kwargs.get("deps", None)
    
    if len(args) == 1 and isinstance(args[0], (list, tuple)) and deps is None:
        deps = map(_get_name, args[0])
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
    elif len(args) != 0:
        raise TaskArgumentError()

    if name is not None:
        t = application.mgr.lookup(name)
        if t is not None:
            t.enhance(deps=deps)

    if action is None: # Need to recurse
        return lambda f: task(f, type=type, name=name, deps=deps)
    
    application.mgr.add_task(type, name, action=action, deps=deps)
    return action

def build(fname, *args, **kwargs):
    type = FileTask if kwargs.get("recreate", True) else FileCreationTask
    return task(*args, type=type, name=fname)

def multitask(func):
    return task(func, type=MultiTask)

class ns(object):
    def __init__(self, *args):
        self.scopes = map(str, args)
    
    def __enter__(self):
        map(application.mgr.push_scope, self.scopes)
        return self

    def __exit__(self, type, value, traceback):
        map(application.mgr.pop_scope, reversed(self.scopes))