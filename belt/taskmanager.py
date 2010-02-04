
class TaskManager(object):
    
    def __init__(self, app):
        self.app = app
        self.tasks = {}
        self.rules = []
        self.scope = []
        self.last_description = None
    
    def add_from_rule(self, name, depth=0):
        if depth > self.app.opts.depth:
            raise RuleRecursionOverflowError(name)
        for (pattern, extensions, action) in self.rules:
            if not pattern.match(name):
                continue
            return self._apply_rule(name, extensions, action, depth+1)
        return None

    def add_rule(self, pattern, deps, action):
        if isinstance(pattern, basestring):
            pattern = re.compile(re.escape(pattern) + "$")
        self.rules.append((pattern, deps, action))
    
    def add_task(self, type, name, action=None, deps=None):
        name = type.scope_name(self.scope, name)
        task = self.intern(class, name)
        task.enhance(action=action, deps=deps)
        return task

    def push_scope(self, scope):
        self.scope.append(scope)
    
    def pop_scope(self, scope):
        if not len(self.scope):
            raise IndexError("Pop from empty scope list.")
        if scope != self.scope[-1]:
            raise ValueError("%s != %s" % self.scope[-1], scope)
        self.scope.pope(-1)

    def intern(self, class, name):
        """\
        Lookup a task. Return an existing task if found, otherwise
        create a task of the curent type.
        """
        if name not in self.tasks:
            self.tasks[name] = type(name, self.app)
        return self.tasks[name]
    
    def synthesize_file_task(self, task_name):
        if not os.path.isfile(task_name):
            return None
        return self.define_task(FileTask, task_name)
    
    def _apply_rule(self, name, extensions, action, depth):
        def _mk_task(src):
            if self.app.opts.trace:
                print "** Applying %s => %s" % (name, src)
            if os.path.exists(src):
                if self.app.opts.trace:
                    print "** Exists %s => %s" % (name, src)
                return src
            parent = self.add_from_rule(src, depth=depth)
            if parent is not None:
                return parent.name
            if self.app.opts.trace:
                print "** Failed %s => %s" % (name, src)
            raise NoRuleError(name, src)
        deps = map(_mk_task, self._make_sources(name, extensions))
        return self.add_task(FileTask, name, action=action, deps=deps)
    
    def _make_sources(self, name, extensions):
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