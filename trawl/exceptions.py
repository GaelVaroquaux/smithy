
class TaskArgumentError(Exception):
    "Illformed task declaration"
    pass

class TaskNotFoundError(KeyError):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Task not found: %s" % self.name

class NoActionForTaskError(RuntimeError):
    "No action can be found or created for a given task."
    pass

class DependencyCycleError(RuntimeError):
    "Cyclic invocation chain."
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Dependency cycle detected at: %s" % self.name

class NoRuleError(Exception):
    "Unable to recursively generate a task for this source."
    pass

class RuleRecursionOverflowError(Exception):
    "Recursion overflow in task selection"
    def __init__(self, *args):
        super(RuleRecursionOverflowError, self).__init__(*args)
        self.targets = []

    def __str__(self):
        base = super(RuleRecursionOverflowError, self).__str__()
        return "%s : [%s]" % (base, ' => '.join(reversed(self.targets)))

    def add_target(self, target):
        self.targets.append(target)

