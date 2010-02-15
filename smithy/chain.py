
from smithy.exceptions import DependencyCycleError

class InvocationChain(object):    
    def __init__(self, chain, task):
        self.parent = chain
        self.known = chain.known.copy()
        if task in self.known:
            raise DependencyCycleError(task)
        self.known.add(task)
        self.task = task
    
    def __str__(self):
        return ', '.join(self.task_names())

    def task_names(self):
        if not self.parent:
            return []
        return self.parent.task_names() + [self.task.name]

class EmptyInvocationChain(InvocationChain):
    def __init__(self):
        self.parent = None
        self.known = set()
        self.task = None
