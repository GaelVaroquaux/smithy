
import t
import belt

@t.root(t.base/"004"/"simple-cycle")
def test_simple_cycle(root):
    src = root/"s"
    def first(tgt, src):
        tgt.write_bytes("a")
    e = belt.Engine()
    belt.build(src, src, e)(first)
    t.raises(RuntimeError, e.run)
    t.eq(src.exists(), False)

@t.root(t.base/"004"/"path-cycle")
def test_path_cycle(root):
    a, b, c = root/"a", root/"b", root/"c"
    def builder(tgt, src):
        pass
    e = belt.Engine()
    belt.build(b, a, e)(builder)
    belt.build(c, b, e)(builder)
    belt.build(a, c, e)(builder)
    t.raises(RuntimeError, e.run)
    map(lambda x: t.eq(x.exists(), False), [a, b, c])
