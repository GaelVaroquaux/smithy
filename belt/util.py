
import hashlib

from path import path

class glob(path):
    def __repr__(self):
        return 'glob(%s)' % path.__repr__(self)

    def sha1(self):
        data = [path(f).sha1() for f in self.glob()]
        return hashlib.sha1(''.join(sorted(data))).hexdigest()