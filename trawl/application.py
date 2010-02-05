
import glob
import optparse as op
import os
import sys

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
        
        if self.opts:
            self.load()

        for t in tasks:
            try:
                task = self.mgr.find(t)
            except NoActionForTaskError:
                raise TaskNotFoundError(t)
            if task is None:
                raise TaskNotFoundError(t)
            task.invoke()

    def load(self):
        load_list = self.find_trawlfiles()
        if len(load_list) == 0:
            self.error("No Trawlfiles found!")
            sys.exit(1)
        print load_list

    def find_trawlfiles(self):
        TRAWL_FILES = "Trawlfile trawlfile Trawfile.py trawfile.py".split()
        load_list = []
        
        # Looking for the entry Trawfile.
        if self.opts.trawlfile is not None:
            TRAWL_FILES = [self.opts.trawlfile]
        for tf in TRAWL_FILES:
            if os.path.isfile(tf):
                load_list.append(tf)
                break

        # Try searching upwards for the main Trawfile
        if not len(load_list) and self.opts.srchup:
            (updir, ignore) = os.path.split(os.getcwd())
            while updir and not len(load_list):
                for tf in TRAWL_FILES:
                    if os.path.exists(os.path.join(updir, tf)):
                        load_list.append(tf)
                        break
                (upupdir, ignore) = os.path.split(updir)
                if upupdir == updir: break
                updir = upupdir

        assert len(load_list) < 2, "Multiple main Trawlfiles: %s" % load_list

        # Main Trawler found, go to its directory
        if len(load_list) == 1:
            dname = os.path.dirname(load_list[0])
            if dname: os.chdir(dname)

        # Load system Trawlfiles
        if self.opts.incsys:
            for fn in glob.glob(self.opts.sysglob):
                load_files.append(fn)
        
        # Load other files
        for fn in glob.glob(self.opts.libglob):
            load_files.append(fn)
            
        return load_list

    def rule_depth(self):
        return getattr(self.opts, "rule_depth", 32)

    def log_output(self, task, rval):
        self._dbg.append((task, rval))

    def is_dry_run(self):
        return getattr(self.opts, "dryrun", False)
    
    def error(self, mesg):
        sys.stderr.write("%s\n" % mesg)
    
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
            metavar="INTEGER",
            help="Maximum recursion depth for rule resolution."),

        op.make_option('-f', dest="trawlfile", default=None, metavar="FILE",
            help="Use FILE as the Trawlfile"),
        op.make_option('-N', dest="srchup", default=True, action='store_false',
            help="Do not search parent directories for a Trawlfile"),
        op.make_option('-G', dest="incsys", default=True, action="store_false",
            help="Ignore system trawlers."),
        op.make_option('-g', dest="sysglob", default="~/.trawl/*.trawl",
            metavar="GLOB",
            help="Import system trawl files. [Default %default]"),
        op.make_option('-L', dest="libglob", default='./trawlers/*.trawl',
            metavar="GLOB",
            help="Import local trawlfiles. [Default %default]"),

        op.make_option('-I', dest="incdir", default=[], action="append",
            metavar="DIR", help="Add DIR to the PYTHONPATH"),
        
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

