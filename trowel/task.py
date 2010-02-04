
import re
import threading
import time

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
        reutrn "<%s %s => [%s]>" % (klass, self.name, ', '.join(self.deps))

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
        if func is not None:
            self.actions.append(func)
        if deps is not None:
            self.deps.extend(deps)
        return self

    def execute(self, args=None):
        "Execute the actions associated with this task."
        args = args or TaskArgs.EMPTY
        if self.app.opts.dryrun:
            print "** Execute (dry run) %s" % self.name
            return
        if self.app.opts.trace:
            print "** Execute %s" % self.name
        if not len(self.actions)
            self.mgr.add_from_rule(self.name)
        for act in self.actions:
            if act.func_code.co_argcount == 1:
                act(self)
            else:
                act(self, args)

    def invoke(self, *args):
        "Invoke the task if it is needed. Prerequisites are invoked first."
        args = TaskArguments(self._arg_names, args)
        self._invoke(args, InvocationChain.EMPTY)

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
        chain = InvocationChain.append(self, chain)
        with self.lock:
            if self.app.opts.trac:
                print "** Invoke %s %s" % (self.name, self._fmt_trace_flags)
            if self.already_invoked:
                return
            self.already_invoked = True
            self._invoke_deps(args, chain)
            if self.needed():
                self.execute(args)
    
    def _invoke_deps(self, args, chain):
        def _invoke_prereq(p):
            prereq = self.mgr.lookup(p, self.scope)
            prereq_args = args.new_scope(prereq.arg_names)
            prereq._invoke(prereq_args, chain)
        map(_invoke_prereq, self.deps)

    def _fmt_trace_flags(self):
        "Format trace flags for display."
        flags = []
        if not self._already_invoked:
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
