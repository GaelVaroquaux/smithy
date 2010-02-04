
import os
import t

@t.test
def test_basic_file():
    fname = t.tmpfname()
    @t.build(fname)
    def build(t):
        open(t.name, "wb").write("o")
    t.app.run(None, [fname])
    t.eq(t.app._dbg, [(fname, None)])
    t.eq(os.path.exists(fname), True)
    t.eq(open(fname).read(), "o")

@t.test
def test_file_as_dep():
    fname = t.tmpfname()
    @t.build(fname)
    def build(t):
        open(t.name, "wb").write("h")
    @t.task([fname])
    def foo():
        return 2
    t.app.run(None, ["foo"])
    t.eq(t.app._dbg, [(fname, None), ("foo", 2)])
    t.eq(os.path.exists(fname), True)
    t.eq(open(fname).read(), "h")

