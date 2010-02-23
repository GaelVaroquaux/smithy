
class SmithyError(Exception):
    pass

class NoBellowsFileError(SmithyError):
    def __str__(self):
        return "Failed to find a Bellows file."

class TaskArgumentError(SmithyError):
    "Illformed task declaration"
    pass

class TaskNotFoundError(KeyError, SmithyError):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Task not found: %s" % self.name

class NoActionForTaskError(RuntimeError, SmithyError):
    "No action can be found or created for a given task."
    pass

class DependencyCycleError(RuntimeError, SmithyError):
    "Cyclic invocation chain."
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return "Dependency cycle detected at: %s" % self.name

class NoRuleError(SmithyError):
    "Unable to recursively generate a task for this source."
    pass

class RuleRecursionOverflowError(SmithyError):
    "Recursion overflow in task selection"
    def __init__(self, *args):
        super(RuleRecursionOverflowError, self).__init__(*args)
        self.targets = []

    def __str__(self):
        base = super(RuleRecursionOverflowError, self).__str__()
        return "%s : [%s]" % (base, ' => '.join(reversed(self.targets)))

    def add_target(self, target):
        self.targets.append(target)

class FileSynthError(SmithyError):
    "A task promised to synth a file but didn't."
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return "File was never created: %s" % self.name
