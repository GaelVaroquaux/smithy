
import os
import re

from trawl.exceptions import \
        TaskNotFoundError, NoActionForTaskError, NoRuleError
from trawl.filetask import FileTask

class TaskManager(object):
    
    def __init__(self, app):
        self.app = app
        self.tasks = {}
        self.rules = []
        self.scope = []
        self.last_description = None
    
    def add_from_rule(self, name, depth=0):
        if depth > self.app.rule_depth():
            raise RuleRecursionOverflowError(name)
        for (pattern, extensions, action) in self.rules:
            if not pattern.search(name):
                continue
            return self._apply_rule(name, extensions, action, depth+1)
        return None

    def add_rule(self, pattern, deps, action):
        if isinstance(pattern, basestring):
            pattern = re.compile(re.escape(pattern) + "$")
        if not isinstance(deps, (list, tuple)):
            deps = [deps]
        self.rules.append((pattern, deps, action))
    
    def add_task(self, type, name, action=None, deps=None):
        name = type.scoped_name(self.scope, name)
        task = self._intern(type, name)
        task.enhance(action=action, deps=deps)
        return task

    def find(self, name, scope=None):
        task = self.lookup(name, scope)
        if task is not None:
            return task
        task = self.add_from_rule(name)
        if task is not None:
            return task
        task = self._make_file_task(name)
        if task is not None:
            return task
        raise NoActionForTaskError(name)

    def lookup(self, name, scope=None):
        curr_scope = scope or self.scope
        curr_scope = curr_scope[:] # Don't change the original
        if name.startswith("trowel:"):
            name = name[len("trowel:"):]
            curr_scope = []
        elif name.startswith("^"):
            while name.startswith("^"):
                if len(curr_scope): curr_scope.pop(-1)
                name = name[1:]
        return self._lookup(name, curr_scope)

    def push_scope(self, scope):
        self.scope.append(scope)
    
    def pop_scope(self, scope):
        if not len(self.scope):
            raise IndexError("Pop from empty scope list.")
        if scope != self.scope[-1]:
            raise ValueError("%s != %s" % self.scope[-1], scope)
        self.scope.pop(-1)
    
    def _intern(self, type, name):
        if name not in self.tasks:
            self.tasks[name] = type(self.app, name)
        return self.tasks[name]
    
    def _lookup(self, name, scopes):
        while len(scopes):
            tn = ':'.join(scopes + [name])
            task = self.tasks.get(tn)
            if task is not None:
                return task
            scopes.pop(-1)
        return self.tasks.get(name)

    def _make_file_task(self, task_name):
        if not os.path.isfile(task_name):
            return None
        return self.add_task(FileTask, task_name)
    
    def _apply_rule(self, name, extensions, action, depth):
        def _mk_task(src):
            self.app.trace("** Applying %s => %s" % (name, src))
            if os.path.exists(src):
                self.app.trace("** Exists %s => %s" % (name, src))
                return src
            parent = self.add_from_rule(src, depth=depth)
            if parent is not None:
                return parent.name
            self.app.trace("** Failed %s => %s" % (name, src))
            raise NoRuleError(name, src)
        deps = map(_mk_task, self._make_sources(name, extensions))
        return self.add_task(FileTask, name, action=action, deps=deps)
    
    def _make_sources(self, name, extensions):
        print "Make sources: %s" % name
        ret = []
        for ext in extensions:
            if ext[:1] == ".":
                (base, ignore) = os.path.splitext(name)
                ret.append("%s%s" % (base, ext))
            elif callable(ext):
                if ext.func_code.co_argcount == 1:
                    ret.append(ext(name))
                else:
                    ret.append(ext())
            else:
                raise TypeError("Invalid replacement type: %r" % ext)
        return ret