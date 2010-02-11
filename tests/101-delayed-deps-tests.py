
import os
import t

@t.test
def test_not_rebuilt():
    prefile = t.tmpfname("foo.c")
    postfile = t.tmpfname("bar.c")
    src = t.tmpfname()
    tgt = t.tmpfname()
    
    # Make the prefile, if this is the only file
    # available to the mktgt rule, then we know that
    # lazy evaluation was broken
    with open(prefile, "wb") as out:
        out.write("prefile")
    
    @t.build(src)
    def mksrc(task, recreate=True):
        task.name.write_bytes(t.uuid.uuid4().hex)
        postfile.write_bytes("postfile")
    @t.build(tgt, [src, t.FileList(t.DATA_DIR / "*.c")])
    def mktgt(task):
        return sorted(task.sources)
        t.eq(sorted(task.sources), )
        out.write_bytes(data.bytes())

    # Check that postfile doesn't exist yet.
    t.eq(postfile.exists(), False)

    # Run the pipeline, test that target saw the
    # expected sources
    t.app.run(None, [tgt])
    tgt_out = sorted([src, t.DATA_DIR/"foo.c", t.DATA_DIR/"bar.c"])
    t.eq(t.app._dbg, [(src, None), (tgt, tgt_out)])
    
    # Postfile should now exist:
    t.eq(postfile.exists(), True)

    # Rerun without destroying postfile
    t.app.clear()
    t.app.run(None, [tgt])
    tgt_out = sorted([src, t.DATA_DIR/"foo.c", t.DATA_DIR/"bar.c"])
    t.eq(t.app._dbg, [(src, None), (tgt, tgt_out)])
    
    # Create a new file to show that we rebind
    # for each run.
    
    t.tmpfname("zoo.c").write_bytes("postpostfile")
    
    t.app.clear()
    t.app.run(None, [tgt])
    tgt_out = sorted([src, t.DATA_DIR/"foo.c",
                        t.DATA_DIR/"bar.c", t.DATA_DIR/"zoo.c"])
    t.eq(t.app._dbg, [(src, None), (tgt, tgt_out)])
    