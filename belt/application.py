
import optparse as op

class Application(object):
    def __init__(self):
        self.mgr = TaskManager(self)
        self.opts = None
        self.args = []

    def run(self, opts, args):
        self.opts, self.args = opts, args

application = Application()

def options():
    return [
        op.make_option('--dry-run', '-n', default=False, action="store_true",
            help="Do a dry run without executing actions."),

        op.make_option('--tasks', '-T', default=None, meta="PATTERN",
            help="List the tasks matching PATTERN, then exit."),
        op.make_option('--deps', '-d', default=False, action="store_true",
            help="Display the tasks and dependencies, then exit."),

        op.make_option('--trowlfile', '-f', default=None, meta="FILE"
            help="Use FILE as the Trowlfile"),
        op.make_option('--trowl-lib', '-T', default='trowllib', meta="DIR",
            help="Auto-import any .trowl files in DIR. [Default %default]"),

        op.make_option('--no-search', '-N', default=False, action='store_true',
            help="Do not search parent directories for a Trowlfile"),
        op.make_option('--system', '-g', default=None, meta="DIR",
            help="Use a system (global) trowlfiles [Default ~/.trowl/*.trowl]"),
        op.make_option('--no-system', '-G', default=False, action="store_false",
            help="Ignore system trowlfiles."),
        
        op.make_option('--rules', default=False, action="store_true",
            help="Trace rule resolution steps."),
        op.make_option('--trace', '-t', default=False, action="store_true",
            help="Turn on task execution tracing."),
        op.make_option('--verbose', '-v', default=False, action="store_true",
            help="Log messages to standard output."),
        op.make_option('--quiet', '-q', default=False, action="store_true",
            help="Do not log messages to standard output."),
        op.make_option('--silent', '-s', default=False, action="store_true",
            help="Supress more messages than quiet.")
    ]

def main():
    global application
    parser = op.OptionParser(usage=__usage__, option_list=options())
    opts, args = parser.parse_args()
    application.run(opts, args)

