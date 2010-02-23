# Copyright 2010 Paul J. Davis <paul.joseph.davis@gmail.com>
#
# This file is part of the Smithy package released under the MIT license.

import os
import t

@t.test
def test_synth_file():
    fname = t.tmpfname()
    @t.synth()
    def synth(t):
        t.synth(fname)
        fname.write_bytes("o")
    t.app.run(None, ["synth"])
    t.eq(t.app._dbg, [("synth", None)])
    t.eq(fname.exists(), True)
    t.eq(fname.bytes(), "o")

@t.test
def test_synth_with_dep():
    base = t.tmpfname()
    src = t.tmpfname()
    tgt = t.tmpfname()
    base.write_bytes("s")
    @t.build(src, [base])
    def mkdep(task, recreate=False):
        open(task.name, "wb").write("o")
    @t.synth([src])
    def synth(task):
        task.synth(tgt)
        tgt.write_bytes(src.bytes() + "n")
    t.app.run(None, ["synth"])
    t.eq(t.app._dbg, [(src, None), ("synth", None)])
    t.eq(src.bytes(), "o")
    t.eq(tgt.bytes(), "on")

    # Rerun
    t.app.clear()
    t.app.run(None, ["synth"])
    t.eq(t.app._dbg, [])

@t.test
def test_dep_on_synth():
    src = t.tmpfname()
    tgt = t.tmpfname()
    @t.synth()
    def synthdep(task):
        task.synth(src)
        src.write_bytes("fo")
    @t.build(tgt, [synthdep])
    def withdep(task):
        task.name.write_bytes(task.source.bytes() + "o")
    
    t.app.run(None, [tgt])
    t.eq(t.app._dbg, [("synthdep", None), (tgt, None)])
    t.eq(src.bytes(), "fo")
    t.eq(tgt.bytes(), "foo")

@t.test
def test_not_synthed():
    @t.synth()
    def synth(task):
        task.synth(t.tmpfname())
    
    t.raises(t.FileSynthError, t.app.run, None, ["synth"])
    