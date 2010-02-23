
import os

from smithy.const import EARLY
from smithy.exceptions import FileSynthError
from smithy.filelist import FileList
from smithy.task import Task

class FileTask(Task):

    @classmethod
    def scoped_name(klass, scope, task_name):
        return task_name
    
    def as_sources(self):
        return [self.name]
    
    def needed(self):
        if not os.path.exists(self.name):
            return True
        if len(self.deps) == 0:
            return True
        our_stamp = self.timestamp()
        for d in self.deps:
            task = self.mgr.find(d)
            if not isinstance(task, FileTask):
                return True
            elif task.timestamp() > our_stamp:
                return True
        return False

    def timestamp(self):
        if os.path.exists(self.name):
            return os.stat(self.name).st_mtime
        return EARLY
    
class FileCreationTask(FileTask):
    
    def needed(self):
        return not os.path.exists(self.name)
    
    def timestamp(self):
        if os.path.exists(self.name):
            return os.stat(self.name).st_mtime
        return EARLY

class FileSynthTask(FileTask):
    
    def __init__(self, *args, **kwargs):
        super(FileSynthTask, self).__init__(*args, **kwargs)
        self.synthed = []
    
    def as_sources(self):
        return self.synthed
    
    def synth(self, filename):
        self.synthed.append(filename)

    def execute(self, args=None):
        ret = super(FileSynthTask, self).execute(args=args)
        for fn in self.synthed:
            if not os.path.exists(fn):
                raise FileSynthError(fn)
        return ret

    def needed(self):
        if len(self.deps) == 0:
            return True
        our_stamp = self.timestamp()
        for d in self.deps:
            task = self.mgr.find(d)
            if not isinstance(task, FileTask):
                return True
            elif task.timestamp() > our_stamp:
                return True
        return False

    def timestamp(self):
        ts = EARLY
        for fn in self.synthed:
            if not os.path.exists(fn):
                raise FileSynthError(fn)
            ts = max(ts, os.stat(fn).st_mtime)
        return ts
