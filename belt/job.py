
import hashlib
import logging
import uuid

from path import path
from sources import Source, make_source

log = logging.getLogger(__name__)

class Job(object):
    def __init__(self, func, src, tgts=None, args=None):
        self.id = uuid.uuid4().hex
        self.func = func

        if not isinstance(src, Source):
            raise TypeError("src must be an instance of Source")
        self.src = src

        self.tgts = tgts
        if self.tgts is None:
            self.tgts = []

        self.args = args
        if self.args is None:
            self.args = []

        self.has_run = False

    @property
    def name(self):
        ret = filter(None, [self.func.__module__, self.func.__name__])
        return '.'.join(ret)

    def runnable(self):
        """\
        Return True if this job can be run, False otherwise.
        """
        return self.src.available()

    def should_run(self):
        """\
        Returns True, False or a dict of filename->hashes to check
        if this job needs to run.
        """
        srcs = self.src.paths()
        if srcs is None:
            return True
        srcids = [s.sha1() for s in srcs]
        ret = {}
        tgts = self.tgts
        if tgts == []:
            return True
        if isinstance(tgts, path):
            tgts = [tgts]
        for t in tgts:
            if not t.exists():
                return True
            ret[t] = self.hash_id([t.sha1()] + srcids)
        return ret

    def run(self):
        args = [self.src.paths(), self.tgts] + self.args
        log.info("Sources: %s" % ', '.join(self.src.paths()))
        log.info("Targets: %s" % ', '.join([t.name for t in self.tgts]))
        if len(self.args):
            log.info("Args: %s" % ', '.join(map(str, args)))
        self.func(self, *args)
        self.has_run = True

    def add_target(self, p):
        if not isinstance(p, path):
            raise TypeError("A target must be an instance of path.")
        if p not in self.tgts:
            self.tgts.append(p)

    def hash_id(self, hids):
        data = ''.join(sorted(hids))
        return hashlib.sha1(data).hexdigest()
    
    def fmt_args(self, args):
        ret = []
        if args[0] is not None:
            ret.append([s.name for s in args[0]])
        else:
            ret.append(None)
        if args[1] is not None:
            ret.append([t.name for t in args[1]])
        else:
            ret.append(None)
        ret.extend(args[2:])
        return ', '.join(map(str, ret))
        