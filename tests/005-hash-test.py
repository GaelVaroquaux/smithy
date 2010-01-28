import time

import t
import belt

@t.root(t.base/"005"/"sigs-ok")
def test_sigs_ok(root):
    """\
    Changing the content of source files
    updates the sha1 and triggers builders
    that depend on the altered files.
    """
    src, tgt = root/"s", root/"t"
    src.dirname().makedirs()
    def first(tgt, src):
        tgt.write_bytes(src.bytes() + "z")
    def build():
        e = belt.Engine()
        belt.build(tgt, src, e)(first)
        e.run()

    src.write_bytes("a")    
    build()
    t.eq(tgt.bytes(), "az")
    mtime = tgt.mtime
    time.sleep(1.5)

    src.write_bytes("b")
    build()
    t.eq(tgt.bytes(), "bz")
    t.gt(tgt.mtime, mtime)
    mtime = tgt.mtime

    build()
    t.eq(tgt.bytes(), "bz")
    t.eq(tgt.mtime, mtime)

@t.root(t.base/"005"/"sigs-used")
def test_sigs_used(root):
    """\
    Rebuilding an intermediate file that has the
    same sha1 does not trigger builders that
    depend on the rebuilt file.
    """
    src, mid, tgt = root/"s", root/"m", root/"t"
    src.dirname().makedirs()
    def first(tgt, src):
        tgt.write_bytes(src.bytes() + "z")
    def second(tgt, src):
        tgt.write_bytes(src.bytes() + "-")
    def build():
        e = belt.Engine()
        belt.build(mid, src, e)(first)
        belt.build(tgt, mid, e)(second)
        e.run()

    src.write_bytes("a")    
    build()
    t.eq(mid.bytes(), "az")
    t.eq(tgt.bytes(), "az-")

    mid.remove()
    time.sleep(1.5)

    build()
    t.eq(mid.bytes(), "az")
    t.eq(tgt.bytes(), "az-")
    t.gt(mid.mtime, tgt.mtime)
