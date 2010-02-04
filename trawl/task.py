
import re
import threading
import time

from trawl.chain import InvocationChain, EmptyInvocationChain

class Task(object):
    def __init__(self, app, name):
        self.app = app
        self.mgr = app.mgr
        self.scope = app.mgr.scope[:]
        self.name = name
        self.sources = []
        self.deps = []
        self.actions = []
        self.already_invoked = False
        self.lock = threading.RLock()

    def __str__(self):
        return self.name
    
    def __repr__(self):
        klass = self.__class__.__name__
        return "<%s %s => [%s]>" % (klass, self.name, ', '.join(self.deps))

    @staticmethod
    def scoped_name(scope, task_name):
        return ":".join(scope + [task_name])
    
    @property
    def source(self):
        "The first source or None if no sources exist."
        if len(self.sources):
            return self.sources[0]
        return None

    def clear(self):
        "Clear the existing prerequisites and actions of this task."
        while len(self.actions):
            self.actions.pop()
        while len(self.deps):
            self.deps.pop()
        return self

    def enhance(self, action=None, deps=None):
        "Add an action and/or dependencies to this task."
        if action is not None:
            self.actions.append(action)
        if deps is not None:
            self.deps.extend(deps)
        return self

    def execute(self, args=None):
        "Execute the actions associated with this task."
        args = args or tuple() #TaskArgs.EMPTY
        if self.app.is_dry_run():
            print "** Execute (dry run) %s" % self.name
            return
        self.app.trace("** Execute %s" % self.name)
        if not len(self.actions):
            self.mgr.add_from_rule(self.name)
        for act in self.actions:
            if act.func_code.co_argcount == 0:
                ret = act()
            elif act.func_code.co_argcount == 1:
                ret = act(self)
            else:
                ret = act(self, *args)
            self.app.log_output(self.name, ret)

    def invoke(self, *args):
        "Invoke the task if it is needed. Prerequisites are invoked first."
        #args = TaskArguments(self.arg_names, args)
        self._invoke(args, EmptyInvocationChain())

    def needed(self):
        "Is this task needed?"
        return True
    
    def reenable(self):
        "Allow this task to be invoked again even if it has already run."
        self.already_invoked = False

    def timestamp(self):
        """\
        The timestamp for this task. Basic tasks return the current time for
        their timestamp. Other tasks can be more sophisticated.
        """
        ts = map(lambda d: self.mgr.lookup(d).timestamp(), self.deps)
        if len(ts):
            return max(ts)
        return time.time()
    
    def _invoke(self, args, chain):
        chain = InvocationChain(chain, self)
        self.app.trace("** Chain: %s" % chain)
        with self.lock:
            self.app.trace("** Invoke %s %s" % (self.name, self._trace_info()))
            if self.already_invoked:
                return
            self.already_invoked = True
            self._invoke_deps(args, chain)
            if self.needed():
                self.execute(args)
    
    def _invoke_deps(self, args, chain):
        self.app.trace("** Deps: %s" % ', '.join(self.deps))
        def _invoke_dep(p):
            prereq = self.mgr.lookup(p, self.scope)
            #prereq_args = args.new_scope(prereq.arg_names)
            prereq._invoke(args, chain)
        map(_invoke_dep, self.deps)

    def _trace_info(self):
        "Format trace flags for display."
        flags = []
        if not self.already_invoked:
            flags.append("first_time")
        if not self.needed():
            flags.append("not_needed")
        if len(flags):
            return "(%s)" % ', '.join(flags)
        return ""
    
    def dump(self):
        """\
        Return a string describing the internal state of this task. Useful
        for debugging.
        """
        result = ["-" * 40]
        result.append("Investigation %s" % self.name)
        result.append("class: %s" % self.__class__.__name__)
        result.append("task needed: %s" % self.needed())
        result.append("timestamp: %s" % self.timestamp())
        result.append("pre-requisites: ")
        prereqs = map(lambda p: self.mgr.lookup(p), self._prereqs)
        prereqs.sort(cmp=lambda a, b: cmp(a.timestamp(), b.timestamp()))
        for req in prereqs:
            result.append("--%s (%s)" % req.name, req.timestamp())
        result.append("." * 40)
        result.extend(["", ""])
        return '\n'.join(result)
