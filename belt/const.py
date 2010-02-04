
class Early(object):
    "An object that sorts before all other objects."
    def __str__(self):
        return "<EARLY TIME>"

    def __cmp__(self, other):
        return -1

EARLY = Early()
