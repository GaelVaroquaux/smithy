
import anydbm
import atexit
import hashlib
import imp
import logging

import pprint

from builder import ImplicitBuilder
from path import path
from util import glob

log = logging.getLogger(__name__)

class Engine(object):
    def __init__(self):
        self.globals = {}
        self.builders = {}
        self.signatures = anydbm.open(".belt-sigs", "c")
        self.curr_mod = None

    def close(self):
        self.signatures.close()

    def load(self, basedir):
        for p in basedir.walk(pattern="*.py"):
            self.curr_mod = '.'.join(basedir.relpathto(p).splitall()[1:-1])
            self.globals[p] = {'__file__': p.basename()}
            code = compile(p.bytes(), p, 'exec')
            exec code in self.globals[p]
        return self

    def add(self, builder):
        builder.module(self.curr_mod)
        for t in builder.targets():
            if t in self.builders:
                raise ValueError("Builder already exists for: %s" % t)
            self.builders[t] = builder
        return self

    def run(self):
        self.root_graph()
        for b in self.walk():
            if self.needs_built(b):
                b.build()
            else:
                b.skip()
            shashes = [self.signatures[s] for s in b.sources()]
            for t in b.targets():
                thash = t.sha1()
                if thash is None:
                    raise RuntimeError("Builder did not produce: %s" % t)
                self.signatures[t] = self.hash(shashes + [t.sha1()])

    def root_graph(self):
        sources = set()
        targets = set()
        for b in self.builders.itervalues():
            if len(b.sources()):
                sources.update(b.sources())
                targets.update(b.targets())
            else:
                sources.update(b.targets())
        initial = sources.difference(targets)
        if len(initial) == 0:
            raise RuntimeError("No initial builders available.")
        for i in initial:
            if i in self.builders:
                continue
            self.builders[i] = ImplicitBuilder(i)

    def walk(self):
        builders = set(self.builders.values())
        while True:
            if not len(builders):
                raise StopIteration()
            ret = None
            for b in builders:
                if self.can_run(b):
                    ret = b
                    break
            if ret is None:
                raise RuntimeError("Unable to continue pipeline.")
            builders.discard(ret)
            yield ret

    def can_run(self, builder):
        for s in builder.sources():
            if s not in self.builders:
                continue
            if not self.builders[s].finished():
                return False
        return True
    
    def needs_built(self, b):
        if len(b.sources()) == 0:
            return True
        shashes = [self.signatures[s] for s in b.sources()]
        for t in b.targets():
            thash = t.sha1()
            if thash is None:
                return True
            thash = self.hash(shashes + [thash])
            if thash != self.signatures.get(t):
                return True
        return False

    def hash(self, hashes):
        data = ''.join(sorted(hashes))
        return hashlib.sha1(data).hexdigest()
