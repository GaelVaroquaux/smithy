
class TrawlError(Exception):
    pass

class NoTrawlfileError(TrawlError):
    def __str__(self):
        return "Failed to find a Trawlfile."

class TaskArgumentError(TrawlError):
    "Illformed task declaration"
    pass

class TaskNotFoundError(KeyError, TrawlError):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Task not found: %s" % self.name

class NoActionForTaskError(RuntimeError, TrawlError):
    "No action can be found or created for a given task."
    pass

class DependencyCycleError(RuntimeError, TrawlError):
    "Cyclic invocation chain."
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Dependency cycle detected at: %s" % self.name

class NoRuleError(TrawlError):
    "Unable to recursively generate a task for this source."
    pass

class RuleRecursionOverflowError(TrawlError):
    "Recursion overflow in task selection"
    def __init__(self, *args):
        super(RuleRecursionOverflowError, self).__init__(*args)
        self.targets = []

    def __str__(self):
        base = super(RuleRecursionOverflowError, self).__str__()
        return "%s : [%s]" % (base, ' => '.join(reversed(self.targets)))

    def add_target(self, target):
        self.targets.append(target)

