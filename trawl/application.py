
import glob
import optparse as op
import os
import re
import sys

from trawl.taskmanager import TaskManager
import trawl.exceptions as exc

__usage__ = "[OPTIONS] task1 [task2 ...]"

class Application(object):
    def __init__(self):
        self.mgr = TaskManager(self)
        self.opts = None
        self.globals = {}
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
            if self.opts.list:
                self.display_tasks(tasks)
                exit(0)

        if len(tasks) == 0:
            print "No task specified."
            exit(0)

        for t in tasks:
            try:
                task = self.mgr.find(t)
            except exc.NoActionForTaskError:
                raise exc.TaskNotFoundError(t)
            if task is None:
                raise exc.TaskNotFoundError(t)
            task.invoke()

    def load(self):
        # Add Python paths
        for dn in self.opts.incdirs:
            sys.path.insert(0, dn)
        # Load the main file.
        self.load_file(self.find_trawlfile())
        # Load system and library tasks
        if self.opts.incsys:
            for fn in glob.glob(self.opts.sysglob):
                self.load_file(fn)
        for fn in glob.glob(self.opts.libglob):
            self.load_file(fn)

    def load_file(self, fname):
        self.globals[fname] = self.init_globals(fname)
        with open(fname) as handle:
            src = handle.read()
        code = compile(src, fname, 'exec')
        exec code in self.globals[fname]
    
    def init_globals(self, fname):
        import trawl.decorators as dec
        return {
            "__file__": fname,
            "task": dec.task,
            "rule": dec.rule,
            "build": dec.build,
            "multitask": dec.multitask,
            "ns": dec.ns
        }

    def find_trawlfile(self):
        TRAWL_FILES = "Trawlfile trawlfile Trawfile.py trawfile.py".split()
        load_list = []
        
        # Looking for the entry Trawfile.
        if self.opts.trawlfile is not None:
            TRAWL_FILES = [self.opts.trawlfile]
        for tf in TRAWL_FILES:
            if os.path.isfile(tf):
                return tf

        # Try searching upwards for the main Trawfile
        if not len(load_list) and self.opts.srchup:
            (updir, ignore) = os.path.split(os.getcwd())
            while updir and not len(load_list):
                for tf in TRAWL_FILES:
                    if os.path.exists(os.path.join(updir, tf)):
                        return tf
                (upupdir, ignore) = os.path.split(updir)
                if upupdir == updir: break
                updir = upupdir
        
        raise exc.NoTrawlfileError()
    
    def display_tasks(self, patterns):
        names = sorted(self.mgr.tasks.keys())
        if len(patterns):
            patterns = map(re.compile, patterns)
            for name in names:
                if any(map(lambda p: p.search(name), patterns)):
                    print repr(self.mgr.tasks[name])
        else:
            for name in names:
                print repr(self.mgr.tasks[name])

    def is_dry_run(self):
        return getattr(self.opts, "dryrun", False)

    def rule_depth(self):
        return getattr(self.opts, "rule_depth", 32)

    def log_output(self, task, rval):
        "For debugging task execution in tests."
        self._dbg.append((task, rval))

    def trace(self, mesg):
        # Weird logic to let tests trace with no opts
        if self.opts and not self.opts.trace:
            return
        self.log(mesg)
    
    def log(self, mesg):
        # Weird logic to let tests log with no opts
        if self.opts and not self.opts.verbose:
            return
        # Let nosetests capture output.
        if not self.opts:
            sys.stdout.write("%s\n" % mesg)
        else:
            sys.stderr.write("%s\n" % mesg)
    

application = Application()

def options():
    return [
        op.make_option('-n', dest="dryrun", default=False, action="store_true",
            help="Do a dry run without executing actions."),

        op.make_option('-T', dest="list", default=False, action='store_true',
            metavar="PATTERN",
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

        op.make_option('-I', dest="incdirs", default=[], action="append",
            metavar="DIR", help="Add DIR to the PYTHONPATH"),

        op.make_option('-t', dest="trace", default=False, action="store_true",
            help="Enable task execution tracing."),
        op.make_option('-v', dest="verbose", default=True, action="store_true",
            help="Display log message on stderr."),
        op.make_option('-q', dest="verbose", action="store_false",
            help="Do not display log message on stderr.")
    ]

def main():
    global application
    parser = op.OptionParser(usage=__usage__, option_list=options())
    opts, args = parser.parse_args()
    try:
        application.run(opts, args)
    except exc.TrawlError, e:
        print str(e)

