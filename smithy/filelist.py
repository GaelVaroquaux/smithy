
import copy
import functools
import glob
import os
import re

from smithy.path import aspath, path

def _exclude_cores(fn):
    return re.search(r"(^|[\/\\])core$", fn) and not os.path.isdir(fn)

class FileListIter(object):
    def __init__(self, source):
        self.source = source
    def next(self):
        return aspath(self.source.next())

class FileList(object):
    """\
    A FileList is essentially an special class for dealing with lists of
    file names.
    
    FileLists are lazy. When given a list of glob patterns for possible
    files to be included in the file list, instead of search the file
    structures to find the files, a FileList holds the pattern for latter use.
    
    This allows us to define a number of patterns to match any number of
    files, but only search out the actual files when the FileList itself
    is actually used.
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
        if len(patterns) == 1 and isinstance(patterns[0], FileList):
            other = patterns[0]
            self._items = copy.copy(other._items)
            self._pending_add = copy.copy(other._pending_add)
            self._pending = other._pending
            self._exclude_patterns = copy.copy(other._exclude_patterns)
            self._exclude_funcs = copy.copy(other._exclude_funcs)
            self._exclude_regexps = copy.copy(other._exclude_regexps)
        else:
            self._items = []
            self._pending_add = []
            self._pending = False
            self._exclude_patterns = FileList.DEFAULT_EXCLUDE_PATTERNS[:]
            self._exclude_funcs = FileList.DEFAULT_EXCLUDE_FUNCS[:]
            self._exclude_regexps = []
            map(self.include, patterns)
    
    # Not hashable
    
    __hash__ = None
    
    # Printing functions
    
    def __str__(self):
        self.resolve()
        return '[%s]' % ', '.join(map(str, self))
    
    def __repr__(self):
        return "<FileList %s>" % str(self)
    
    # Binary operator methods
    
    def __add__(self, other):
        print "Adding: %r" % other
        if not isinstance(other, (list, FileList)):
            return NotImplemented
        elif isinstance(other, FileList):
            self.resolve()
            other.resolve()
            self._items += map(aspath, other._items)
        else:
            self.resolve()
            self._items += map(aspath, other)
        return self
    
    def __radd__(self, other):
        if not isinstance(other, (list, FileList)):
            return NotImplemented
        elif isinstance(other, FileList):
            self.resolve()
            other.resolve
            self._items = other._items + self._items
        else:
            self.resolve()
            self._items = map(aspath, other) + self._items
        return self

    # Container Methods

    def __len__(self):
        self.resolve()
        return len(self._items)

    def __iter__(self):
        self.resolve()
        return FileListIter(iter(self._items))

    def __getitem__(self, item):
        self.resolve()
        if not isinstance(item, slice):
            return aspath(self._items[item])
        ret = FileList(self)
        ret._items = self._items[item]
        return ret

    def __setitem__(self, item, value):
        self.resolve()
        if not isinstance(item, slice):
            self._items[item] = aspath(value)
        elif isinstance(value, list):
            self._items[item] = map(aspath, value)
        elif isinstance(value, FileList):
            value.resolve()
            self._items[item] = value._items
        else:
            raise TypeError("%r is not an instance of list or FileList")

    def __delitem__(self, item):
        self.resolve()
        del self._items[item]

    def __contains__(self, item):
        self.resolve()
        return aspath(item) in self._items
    
    # Comparison functions
    
    def __lt__(self, other):
        if isinstance(other, FileList):
            self.resolve()
            other.resolve()
            return self._items < other._items
        elif isinstance(other, list):
            self.resolve()
            return self._items < other
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, FileList):
            self.resolve()
            other.resolve()
            return self._items <= other._items
        elif isinstance(other, list):
            self.resolve()
            return self._items <= other
        return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, FileList): 
            self.resolve()
            other.resolve()
            return self._items == other._items
        elif isinstance(other, list):
            self.resolve()
            return self._items == other
        return NotImplemented
    
    def __ne__(self, other):
        if isinstance(other, FileList):
            self.resolve()
            other.resolve()
            return self._items != other._items
        elif isinstance(other, list):
            self.resolve()
            return self._items != other
        return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, FileList):
            self.resolve()
            other.resolve()
            return self._items >= other._items
        elif isinstance(other, list):
            self.resolve()
            return self._items >= other
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, FileList):
            self.resolve()
            other.resolve()
            return self._items >= other._items
        elif isinstance(other, list):
            self.resolve()
            return self._items >= other
        return NotImplemented

    # List interface functions.

    def append(self, obj):
        self.resolve()
        self._items.append(aspath(obj))
    
    def count(self, obj):
        self.resolve()
        return self._items.count(aspath(obj))
    
    def extend(self, iterobj):
        self.resolve()
        self._items.extend(aspath(p) for p in iterobj)
    
    def index(self, obj, *args):
        self.resolve()
        return self._items.index(aspath(obj), *args)

    def insert(self, index, obj):
        self.resolve()
        self._items.insert(index, aspath(obj))

    def pop(self, index):
        self.resolve()
        return aspath(self._items.pop(index))

    def remove(self, obj):
        self.resolve()
        self._items.remove(aspath(obj))

    def reverse(self):
        self.resolve()
        self._items.reverse()
    
    def sort(self, *args, **kwargs):
        self.resolve()
        self._items.sort(*args, **kwargs)

    # FileList extension functions.

    def copy(self):
        "Return a cloned instance of this FileList"
        return self.__class__(self)

    def expand(self):
        ret = self.__class__(self)
        ret.resolve()
        return ret

    def include(self, *patterns):
        """\
        Add new glob patterns to this FileList instance. If an aray is given,
        add each element of the array.
        
        Example:
          file_list.include("*.rb", "*.cfg")
          file_list.include("math.c lib.h *.o".split())
        """
        for p in patterns:
            if isinstance(p, basestring):
                self._pending_add.append(p)
            else:
                map(self.include, p)
        self._pending = True
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
                self._exclude_patterns.append(p)
            elif callable(p):
                self._exclude_funcs.append(p)
            else:
                map(self.exclude, p)
        if not self._pending:
            self._resolve_excludes()
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
                self._exclude_patterns.append(re.compile(p))
            elif hasattr(p, "pattern") and hasattr(p, "search"):
                # Can't find a better test for a compiled regular expression
                self._exclude_patterns.append(p)
            else:
                map(self.exclude_re, p)
        if not self._pending:
            self._resolve_excludes()
        return self
    
    def is_excluded(self, fn):
        "Should the given filename be excluded?"
        if not self._exclude_regexps:
            self._calculate_exclude_regexp()
        if any(r.search(fn) for r in self._exclude_regexps):
            return True
        return any(func(fn) for func in self._exclude_funcs)
    
    def clear_excludes(self):
        "Clear all the exclude patterns."
        self._exclude_patterns = []
        self._exclude_funcs = []
        if not self._pending:
            self._calculate_exclude_regexp()
        return self

    def resolve(self):
        "Resolve all the pending glob patterns."
        if self._pending:
            self._pending = False
            for fn in self._pending_add:
                self._resolve_add(fn)
            self._pending_add = []
            self._resolve_excludes()
        return self

    def sub(self, pattern, repl):
        """\
        Calls re.sub(pattern, repl, fn) on each filename.

        Triggers file name resolution.
        """
        self.resolve()
        p = re.compile(pattern)
        for idx in range(len(self)):
            self[idx] = p.sub(repl, self[idx])
        return self

    def exist(self):
        """\
        Remove any file names that don't exist on the file system.
        
        Triggers file name resolution.
        """
        self.resolve()
        idx = 0
        while idx < len(self):
            if not self[idx].exists():
                self.pop(idx)
            else:
                idx += 1
        return self

    def _resolve_add(self, fn):
        if re.search(r"[*?\[\{]", fn):
            self._add_matching(fn)
        else:
            self.append(aspath(fn))

    def _add_matching(self, pattern):
        "Add files matching the glob pattern."
        fnames = filter(lambda fn: not self.is_excluded(fn), glob.glob(pattern))
        self.extend(aspath(fn) for fn in fnames)

    def _exclude(self, fn):
        "Should the given filename be excluded?"
        if not self._exclude_regexps:
            self._calculate_exclude_regexp()
        if any(r.search(fn) for r in self._exclude_regexps):
            return True
        return any(func(fn) for func in self._exclude_funcs)
    
    def _resolve_excludes(self):
        self._calculate_exclude_regexp()
        idx = 0
        while idx < len(self):
            if self.is_excluded(self[idx]):
                self.pop(idx)
            else:
                idx += 1

    def _calculate_exclude_regexp(self):
        self._exclude_regexps = []
        for e in self._exclude_patterns:
            if hasattr(e, "pattern") and hasattr(e, "search"):
                self._exclude_regexps.append(e)
            elif re.search(r"[*?]", e):
                for fn in glob.glob(e):
                    self._exclude_regexps.append(re.compile(fn))
            else:
                self._exclude_regexps.append(re.compile(e))
