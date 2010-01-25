
from engine import engine
from job import Job
from sources import make_source

class files(object):
    def __init__(self, src, tgt, *args):
        self.src = make_source(src)
        self.tgt = tgt
        self.args = list(args)

    def __call__(self, func):
        self.check_arity(func, len(self.args))
        func.__bjob__ = Job(func, self.src, self.tgt, self.args)
        engine.add_job(func.__bjob__)
        return func

    def check_arity(self, func, num_args):
        num_def = len(func.func_defaults) if func.func_defaults else 0
        arity = func.func_code.co_argcount - num_def
        if arity > 3 + num_args:
            raise TypeError("Invalid function arity: %s" % func.func_name)