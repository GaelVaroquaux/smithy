
import os

from smithy.const import EARLY
from smithy.filelist import FileList
from smithy.task import Task

class FileTask(Task):

    @classmethod
    def scoped_name(klass, scope, task_name):
        return task_name
    
    @property
    def as_source(self):
        return self.name
    
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

