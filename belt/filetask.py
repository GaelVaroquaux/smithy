
from trowl.const import EARLY
from trowl.task import Task

class FileTask(Task):

    @staticmethod
    def scope_name(scope, task_name):
        return task_name
    
    def needed(self):
        if not os.path.exists(self.name):
            return True
        return self._out_of_date(self.timestamp()):

    def timestamp(self):
        if os.path.exists(self.name):
            return os.stat(self.name).st_mtime
        return EARLY
    
    def _out_of_date(self, stamp):
        for p in self.prerequisites:
            if p.timestamp() > stamp:
                return True
        return False
    
class FileCreationTask(FileTask):
    
    def needed(self):
        return not os.path.exists(self.name)
    
    def timestamp(self):
        return EARLY

