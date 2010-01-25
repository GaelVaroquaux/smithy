
import types

from path import path

class Source(object):
    def available(self):
        raise NotImplemented()
    def paths(self):
        raise NotImplemented()

class NoSource(Source):
    def __init__(self):
        pass
    def available(self):
        return True
    def paths(self):
        return None

class FileSource(Source):
    def __init__(self, fname):
        if not isinstance(fname, path):
            raise TypeError("%r is not an instance of path" % fname)
        self.fname = fname
    def available(self):
        return self.fname.exists()
    def paths(self):
        return [self.fname]

class JobSource(Source):
    def __init__(self, job):
        from job import Job
        if not isinstance(job, Job):
            raise TypeError("%r is not an instance of Job" % job)
        self.job = job
    def available(self):
        return self.job.has_run
    def paths(self):
        return self.job.tgts

class ListSource(Source):
    def __init__(self, srcs):
        for s in srcs:
            if not isinstance(s, Source):
                raise TypeError("%r is not an instance of Source" % s)
        self.srcs = srcs
    def available(self):
        l = len(filter(None, (s for s in self.srcs if not s.available())))
        return l == 0

def make_source(src):
    if src is None:
        return NoSource()
    if isinstance(src, path):
        return FileSource(src)
    if isinstance(src, types.FunctionType):
        if not hasattr(src, "__bjob__"):
            raise AttributeError("Function has not been decorated as a job.")
        return JobSource(src.__bjob__)
    ret = map(make_source, src)
    for r in ret:
        if not isinstance(r, (FileSource, JobSource)):
            raise TypeError("%r not an instance of FileSource or JobSource" % r)
    return ret
