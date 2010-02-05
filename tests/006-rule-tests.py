import t

@t.test
def test_basic_rule():
    csrc = t.tmpfname("foo.c")
    cobj = t.tmpfname("foo.o")
    app = t.tmpfname("foo")
    @t.rule(".o", ".c")
    def compile(task):
        open(task.name, "wb").write(open(task.source).read() + "+with_o")
    @t.build(app, [cobj])
    def link(task):
        open(task.name, "wb").write(open(task.source).read() + "+linked")
    open(csrc, "wb").write("source")
    t.app.run(None, [app])
    t.eq(t.app._dbg, [(cobj, None), (app, None)])

@t.test
def test_multi_sources():
    csrcs = [t.tmpfname() + ".c" for i in range(10)]
    cobjs = [fn[:-2] + ".o" for fn in csrcs]
    app = t.tmpfname()
    @t.rule(".o", ".c")
    def compile(task):
        open(task.name, "wb").write(open(task.source).read() + ".o")
    @t.build(app, cobjs)
    def link(task):
        open(task.name, "wb").write(open(task.source).read() + ".exe")
    for cs in csrcs:
        open(cs, "wb").write("source")
    t.app.run(None, [app])
    t.eq(len(t.app._dbg), len(cobjs)+1)
    t.eq(t.app._dbg[0], (cobjs[0], None))
    t.eq(t.app._dbg[-1], (app, None))

def make_chain(depth):
    if depth < 1:
        fname = t.tmpfname()
        open(fname + ".0", "wb").write("ohai!")
        return fname
    @t.rule(".%d" % depth, ".%d" % (depth-1))
    def chained(task):
        open(task.name, "wb").write(open(task.source).read())
    return make_chain(depth-1)

@t.test
def test_chained_rules():
    fname = make_chain(14)
    @t.build(fname + ".15", [fname+".14"])
    def cap(task):
        open(task.name, "wb").write("capped!")
    t.app.run(None, [fname+".15"])
    t.eq(len(t.app._dbg), 15) # .0 is not recorded as run
    t.eq(open(fname+".15").read(), "capped!")