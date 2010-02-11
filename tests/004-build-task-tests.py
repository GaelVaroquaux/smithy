
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

@t.test
def test_file_creation():
    fname = t.tmpfname()
    @t.build(fname, recreate=False)
    def build(task):
        open(task.name, "wb").write(t.uuid.uuid4().hex)
    t.app.run(None, [fname])
    t.eq(t.app._dbg, [(fname, None)])
    t.eq(os.path.exists(fname), True)
    first_run = open(fname).read()
    t.app.clear()
    t.app.run(None, [fname])
    t.eq(t.app._dbg, [])
    t.eq(os.path.exists(fname), True)
    t.eq(open(fname).read(), first_run)

@t.test
def test_not_rebuilt():
    src = t.tmpfname()
    tgt = t.tmpfname()
    @t.build(src, recreate=False)
    def mksrc(task):
        open(task.name, "wb").write(t.uuid.uuid4().hex)
    @t.build(tgt, [src])
    def mktgt(task):
        print task.sources
        print task.source
        open(task.name, "wb").write(open(task.source).read())
    print t.app.mgr.tasks
    t.app.run(None, [tgt])
    t.eq(t.app._dbg, [(src, None), (tgt, None)])
    t.eq(os.path.exists(src), True)
    t.eq(os.path.exists(tgt), True)
    first_run = open(src).read()
    t.eq(open(tgt).read(), first_run)
    t.app.clear()
    t.app.run(None, [tgt])
    t.eq(t.app._dbg, [])
    t.eq(open(src).read(), first_run)
    t.eq(open(tgt).read(), first_run)

@t.test
def test_rerun_build():
    tgt = t.tmpfname()
    @t.build(tgt)
    def mktgt(task):
        task.name.write_bytes("yup")
    
    t.app.run(None, [tgt])
    t.eq(t.app._dbg, [(tgt, None)])
    t.app.clear()
    t.app.run(None, [tgt])
    t.eq(t.app._dbg, [(tgt, None)])

@t.test
def test_dep_not_filetask():
    src = t.tmpfname()
    tgt = t.tmpfname()
    @t.task
    def mksrc(task):
        src.write_bytes("sourcey")
    @t.build(tgt, [mksrc])
    def mktgt(task):
        task.name.write_bytes("yup")
    t.app.run(None, [tgt])
    t.eq(t.app._dbg, [("mksrc", None), (tgt, None)])
    
    t.app.clear()
    t.app.run(None, [tgt])
    t.eq(t.app._dbg, [("mksrc", None), (tgt, None)])

