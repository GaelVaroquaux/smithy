
import optparse as op

from trawl.exceptions import TaskNotFoundError, NoActionForTaskError
from trawl.taskmanager import TaskManager

__usage__ = "[OPTIONS] task1 [task2 ...]"

class Application(object):
    def __init__(self):
        self.mgr = TaskManager(self)
        self.opts = None
        self.args = []
        self._dbg = []

    def clear(self, tasks=False):
        if tasks: self.mgr = TaskManager(self)
        for t in self.mgr.tasks.itervalues():
            t.reenable()
        self._dbg = []

    def run(self, opts, tasks):
        self.opts = opts
        self.setup()
        
        for t in tasks:
            try:
                task = self.mgr.find(t)
            except NoActionForTaskError:
                raise TaskNotFoundError(t)
            if task is None:
                raise TaskNotFoundError(t)
            task.invoke()

    def setup(self):
        pass

    def rule_depth(self):
        return getattr(self.opts, "rule_depth", 32)

    def log_output(self, task, rval):
        self._dbg.append((task, rval))

    def is_dry_run(self):
        return getattr(self.opts, "dryrun", False)
    
    def trace(self, mesg, is_rule=False):
        print mesg

application = Application()

def options():
    return [
        op.make_option('-n', dest="dryrun", default=False, action="store_true",
            help="Do a dry run without executing actions."),

        op.make_option('-T', dest="task_list", default=None, metavar="PATTERN",
            help="List the tasks matching PATTERN, then exit."),
        op.make_option('-d', dest="do_deps", default=False, action="store_true",
            help="Display the tasks and dependencies, then exit."),
        op.make_option('-D', dest='rule_depth', default=32, type='int',
            help="Maximum recursion depth for rule resolution."),

        op.make_option('-f', dest="trawlfile", default=None, metavar="FILE",
            help="Use FILE as the Trawlfile"),
        op.make_option('-L', dest="libdir", default='./trawlers', metavar="DIR",
            help="Auto-import any .trawl files in DIR. [Default %default]"),
        op.make_option('-I', dest="incdir", default=None, metavar="DIR",
            help="Add DIR to the PYTHONPATH"),

        op.make_option('-N', dest="incsys", default=False, action='store_true',
            help="Do not search parent directories for a Trawlfile"),
        op.make_option('-g', dest="sysdir", default=None, metavar="DIR",
            help="Use global trawler files. [Default ~/.trawl/*.trawl]"),
        op.make_option('-G', dest="ignsys", default=False, action="store_false",
            help="Ignore system trawlers."),
        
        op.make_option('-r', dest="rules", default=False, action="store_true",
            help="Trace rule resolution steps."),
        op.make_option('-t', dest="trace", default=False, action="store_true",
            help="Turn on task execution tracing."),
        op.make_option('-v', dest="verbose", default=False, action="store_true",
            help="Log messages to standard output."),
        op.make_option('-q', dest="queit", default=False, action="store_true",
            help="Do not log messages to standard output."),
        op.make_option('-s', dest="silent", default=False, action="store_true",
            help="Supress more messages than quiet.")
    ]

def main():
    global application
    parser = op.OptionParser(usage=__usage__, option_list=options())
    opts, args = parser.parse_args()
    application.run(opts, args)

