
import logging

log = logging.getLogger(__name__)

class Builder(object):
    def __init__(self, func, sources, targets):
        self.func = func
        self.sources = sources
        self.targets = targets
        self.finished = False

    def __repr__(self):
        if not self.func:
            return "<Builder %d>" % id(self)
        name = filter(None, [self.func.__module__, self.func.__name__])
        name = ':'.join(name)
        return "<Builder %r %d>" % (name, id(self))

    def __str__(self):
        name = filter(None, [self.func.__module__, self.func.__name__])
        return ':'.join(name)

    def build(self):
        if not self.func:
            return
        for tgt in self.targets:
            if not tgt.dirname().exists():
                tgt.dirname().makedirs()
        if len(self.targets) == 1:
            args = self.targets + self.sources
        else:
            args = [self.targets] + self.sources            
        self.func(*args)

    def log_parameters(self):
        for src in self.sources:
            log.info("%10s -> %s" % ("", src))
        for tgt in self.targets:
            log.info("%10s <- %s" % ("", tgt))