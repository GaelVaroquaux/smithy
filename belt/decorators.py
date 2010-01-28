
import belt
from path import path
from builder import FunctionBuilder, SourceBuilder

def topath(p):
    if isinstance(p, basestring):
        return [path(p)]
    elif isinstance(p, path):
        return [p]
    else:
        return map(path, p)

class build(object):
    def __init__(self, targets, *sources):
        self.engine = None
        self.targets = topath(targets)
        if len(sources) and isinstance(sources[-1], belt.Engine):
            self.engine = sources[-1]
            self.sources = topath(sources[:-1])
        else:
            self.sources = topath(sources)

    def __call__(self, func):
        builder = FunctionBuilder(func, self.sources, self.targets)
        (self.engine or belt.engine).add(builder)
        return func

class source(object):
    def __init__(self, targets, engine=None):
        self.engine = engine
        self.targets = topath(targets)

    def __call__(self, func):
        help(SourceBuilder)
        builder = SourceBuilder(func, self.targets)
        (self.engine or belt.engine).add(builder)
        return func
