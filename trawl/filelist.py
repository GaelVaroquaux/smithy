
import copy
import glob
import os
import re

def _exclude_cores(fn):
    return fn.search(r"(^|[\/\\])core$", fn) and not os.path.isdir(fn)

class FileList(object):
    """\
    A FileList is essentially an special class for dealing with lists of
    file names.
    
    FileLists are lazy. When given a list of glob patterns for possible
    files to be included in the file list, instead of search the file
    structures to find the files, a FileList holds the pattern for latter use.
    
    This allows us to define a number of patterns to match any number of
    files, but only search out the actual files when the FileList itself
    is actually used. Methods that trigger the resolution to file names are
    documented as such.
    
    Notable special methods that trigger name resolution are:
        `__str__`
        `__eq__`
        `__iter__`
    """
    
    DEFAULT_EXCLUDE_PATTERNS = [
        re.compile(r"(^|[\/\\])CVS([\/\\]|$)"),
        re.compile(r"(^|[\/\\])\.svn([\/\\]|$)"),
        re.compile(r"(^|[\/\\])\.git([\/\\]|$)"),
        re.compile(r"(^|[\/\\])\.hg([\/\\]|$)"),
        re.compile(r"\.bak$"),
        re.compile(r"~$")
    ]
    DEFAULT_EXCLUDE_FUNCS = [
        _exclude_cores
    ]
            
    def __init__(self, *patterns):
        """\
        Create a FileList from the provided globbable patterns. If you
        wish to perform multiple includes or excludes when creating
        new instances, use the method chaining pattern.
        
        Example:
          file_list = FileList("lib/**/*.py", "test/test*.py")
          
          pkg_files = FileList("lib/**/*").exclude_re(r"\bCVS\b")
                        .exclude_re(r"\b.git\b").exclude_re("\b.svn\b")
        """
        self.pending_add = []
        self.pending = False
        self.exclude_patterns = self.DEFAULT_IGNORE_PATTERNS[:]
        self.exclude_funcs = self.DEFAULT_IGNORE_FUNCS[:]
        self.exclude_exps = None
        self.items = []
        map(self.include, patterns)
    
    def __str__(self):
        self.resolve()
        return ' '.join(self.items)
    
    def __eq__(self, other):
        return self.as_array() == other.as_array()

    def __iter__(self):
        self.resolve()
        return iter(self.items)

    def copy(self):
        "Return a cloned instance of this FileList"
        return copy.copy(self)

    def as_array(self):
        """\
        Return the matched filenames as an array.

        Triggers name resolution. (Obviously...)
        """
        self.resolve(self)
        return self.items

    def include(self, *patterns):
        """\
        Add new glob patterns to this FileList instance. If an aray is given,
        add each element of the array.
        
        Example:
          file_list.include("*.rb", "*.cfg")
          file_list.include("math.c lib.h *.o".split())
        """
        for p in patterns:
            if isisntance(p, basestring):
                self.pending_add.append(p)
            else:
                map(self.include, p)
        self.pending = True
        return self

    def exclude(self, *patterns):
        """\
        Register a list of glob patterns that should be excluded from the
        list. Remember that a full pathname is a valid glob if you want
        to exclude specific files.
        
        Note that glob patterns are expanded against the file system. If a
        file is explicitly aded to af ile list, but does not exist on the
        file system, then a glob pattern in the exclude list will not
        exclude the file.
        
        Examples:
          FileList('a.c', 'b.c').exclude('a.c') -> ['b.c']
         
        If "a.c" is a file:
          FileList('a.c', 'b.c').exclude('a.*') -> ['b.c']
         
        If "a.c" is not a file:
          FileList('a.c', 'b.c').exclude('a.*') -> ['a.c', 'b.c']
        
        """
        for p in patterns:
            if isinstance(p, basestring):
                self.exclude_patterns.append(pat)
            else:
                map(self.exclude, p)
        if not self.pending:
            self.resolve_excludes()
        return self
    
    def exclude_re(self, *patterns):
        """\
        Register a list of regular expression patterns or objects that
        should be excluded from the list of file names.
        
        The `search` method is used to compare regular expressions
        to file names which means that you need to explicitly anchor
        patterns with '^' if you want to start at the beginning of
        the string.
        
        Examples:
          FileList('ab.c', 'b.c').exclude_re(r"a.*") -> ['b.c']
          FileList('ab.c', 'b.c').exclude_re(r"^b") -> ['ab.c']
        
        """
        for p in patterns:
            if isinstance(p, basestring):
                self.exclude_patterns.append(re.compile(p))
            elif hasattr(p, "pattern") and hasattr(p, "search"):
                # Can't find a better test for a compiled regular expression
                self.exclude_patterns.append(p)
            else:
                map(self.exclude_reg, p)
        if not self.pending:
            self.resolve_excludes()
        return self
    
    def clear_exclude(self):
        "Clear all the exclude pattersn so that we exclude nothing."
        self.exclude_patters = []
        self.exclude_funcs = []
        if not pending:
            self.calculate_exclude_regexp()
        return self

    def resolve(self):
        "Resolve all the pending glob patterns."
        if self.pending:
            self.pending = False
            for fn in self.pending_add:
                self.resolve_add(fn)
            self.pending_add = []
            self.resolve_exclude()
        return self
    
    def calculate_exclude_regexp(self):
        self.exclude_exps = []
        for e in self.exclude_patterns:
            if hasattr(e, "pattern") and hasattr(e, "search"):
                self.exclude_exps.append(e)
            elif re.search(r"[*?]", e):
                for fn in glob.glob(e):
                    ignores.append(re.compile(fn))
            else:
                ignores.append(re.compile(e))
    
    def _resolve_add(self, fn):
        if re.search(r"[*?\[\{]", fn):
            self._add_matching(fn)
        else:
            self.items.append(fn)
    
    def _resolve_exclude(self):
        self.calculate_exclude_regexp()
        def _filt(fn):
            return not self.exclude_regexp.search(fn)
        self.items = filter(_filt, self.items)

    def sub(self, pattern, repl):
        """\
        Calls re.sub(pattern, repl, fn) on each filename.

        Triggers file name resolution.
        """
        self.resolve()
        p = re.compile(pattern)
        self.items = map(lambda fn: p.sub(repl, fn), self.items)
        return self
    
    def existing(self):
        """\
        Remove any file names that don't exist on the file system.
        """
        self.resolve()
        self.items = filter(lambda fn: os.path.exists(fn), self.items)
        return self
    
    def _add_matching(self, pattern):
        "Add files matching the glob pattern."
        fnames = filter(lambda fn: not self.exclude(fn), glob.glob(pattern))
        self.items.extend(fnames)

    def exclude(self, fn):
        "Should the given filename be excluded?"
        if not self.exclude_exps:
            self.calculate_exclude_regexp()
        if any(r.search(r) for r in self.exclude_exps):
            return True
        return any(func(fn) for func in self.exclude_funcs)
