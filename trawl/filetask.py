
import os

from trawl.const import EARLY
from trawl.task import Task

class FileTask(Task):

    @staticmethod
    def scope_name(scope, task_name):
        return task_name
    
    @property
    def as_source(self):
        return self.name
    
    def needed(self):
        if not os.path.exists(self.name):
            return True
        our_stamp = self.timestamp()
        dep_stamps = map(lambda d: self.mgr.lookup(d).timestamp(), self.deps)
        return any(map(lambda ds: ds > our_stamp, dep_stamps))

    def timestamp(self):
        if os.path.exists(self.name):
            return os.stat(self.name).st_mtime
        return EARLY
    
class FileCreationTask(FileTask):
    
    def needed(self):
        return not os.path.exists(self.name)
    
    def timestamp(self):
        return EARLY

