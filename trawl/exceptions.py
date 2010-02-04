
class TaskArgumentError(Exception):
    "Illformed task declaration"
    pass

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

