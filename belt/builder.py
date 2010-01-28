
import logging

log = logging.getLogger(__name__)

class Builder(object):
    def __init__(self, sources, targets):
        self._sources = sources
        self._targets = targets
        self._finished = False

    def __repr__(self):
        klass = self.__class__.__name__
        return "<%s %r %d>" % (klass, self.name(), id(self))

    def __str__(self):
        return self.name()

    def sources(self):
        return self._sources
    
    def targets(self):
        return self._targets

    def finished(self):
        return self._finished

    def name(self):
        raise NotImplemented()

    def module(self, modname):
        pass

    def log(self, skipped=False):
        raise NotImplemented()

    def build(self):
        raise NotImplemented()

    def skip(self):
        self.log(skipped=True)
        self._finished = True

class ImplicitBuilder(Builder):
    def __init__(self, target):
        super(ImplicitBuilder, self).__init__([], [target])

    def name(self):
        return "%s" % self.targets()[0]

    def build(self):
        self.log()
        if not self.targets()[0].exists():
            tgt = self.targets()[0]
            raise RuntimeError("Source file does not exist: %s" % tgt)
        self._finished = True

    def log(self, skipped=False):
        log.info("%-10s %s" % ("[SOURCE]", self.targets()[0]))

class FunctionBuilder(Builder):
    def __init__(self, func, sources, targets):
        super(FunctionBuilder, self).__init__(sources, targets)
        self.func = func

    def module(self, modname):
        if not self.func.__module__:
            self.func.__module__ = modname

    def name(self):
        name = filter(None, [self.func.__module__, self.func.__name__])
        return ':'.join(name)
    
    def log(self, skipped=False):
        if skipped:
            log.info("%-10s %s" % ("[SKIPPED]", self))
        else:
            log.info("%-10s %s" % ("[BUILD]", self))
            for src in self.sources():
                log.info("%10s -> %s" % ("", src))
            for tgt in self.targets():
                log.info("%10s <- %s" % ("", tgt))
    
    def build(self):
        self.log()
        for tgt in self.targets():
            if not tgt.dirname().exists():
                tgt.dirname().makedirs()
        if len(self.targets()) == 1:
            args = self.targets() + self.sources()
        else:
            args = [self.targets()] + self.sources()
        print args
        self.func(*args)
        self._finished = True
    
class SourceBuilder(FunctionBuilder):
    def __init__(self, func, targets):
        super(SourceBuilder, self).__init__(func, [], targets)

    def name(self):
        return ",".join(self.targets())
