
from engine import engine
from path import path

def topath(p):
    if isinstance(p, path):
        return p
    return path(p)

class build(object):
    def __init__(self, t, *s):
        self.sources = map(topath, s)
        if isinstance(t, basestring):
            self.targets = [topath(t)]
        elif isinstance(t, path):
            self.targets = [t]
        else:
            self.targets = map(topath, t)

    def __call__(self, func):
        engine.add(func, self.sources, self.targets)
        return func
