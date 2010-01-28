
import t
import belt

@t.root(t.base/"002"/"merge")
def test_merge(root):
    src1, src2, tgt = root/"s1", root/"s2", root/"t"
    src1.dirname().makedirs()
    src1.write_bytes("a")
    src2.write_bytes("b")
    def first(tgt, src1, src2):
        tgt.write_bytes(src1.bytes() + src2.bytes())
    e = belt.Engine()
    belt.build(tgt, src1, src2, e)(first)
    e.run()
    t.eq(tgt.bytes(), "ab")

@t.root(t.base/"002"/"split")
def test_split(root):
    src, tgt1, tgt2 = root/"s", root/"t1", root/"t2"
    src.write_bytes("ab")
    def first(tgts, src):
        tgts[0].write_bytes(src.bytes()[0])
        tgts[1].write_bytes(src.bytes()[1])
    e = belt.Engine()
    belt.build([tgt1, tgt2], src, e)(first)
    e.run()
    t.eq(tgt1.bytes(), "a")
    t.eq(tgt2.bytes(), "b")

@t.root(t.base/"002"/"split-merge")
def test_split(root):
    src, mid1, mid2, tgt = root/"a", root/"b", root/"c", root/"d"
    src.dirname().makedirs()
    src.write_bytes("ab")
    def first(tgts, src):
        tgts[0].write_bytes(src.bytes()[0])
        tgts[1].write_bytes(src.bytes()[1])
    def second(tgt, src1, src2):
        tgt.write_bytes(src2.bytes() + src1.bytes())
    e = belt.Engine()
    belt.build([mid1, mid2], src, e)(first)
    belt.build(tgt, mid1, mid2, e)(second)
    e.run()
    t.eq(mid1.bytes(), "a")
    t.eq(mid2.bytes(), "b")
    t.eq(tgt.bytes(), "ba")
