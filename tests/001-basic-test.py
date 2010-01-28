
import t
import belt

@t.root(t.base/"001"/"source")
def test_simple(root):
    tgt = root/"a"
    def first(target):
        target.write_text("a")
    e = belt.Engine()
    belt.source(tgt, e)(first)
    e.run()
    t.eq(tgt.bytes(), "a")

@t.root(t.base/"001"/"implict")
def test_implicit(root):
    src, tgt = root/"a", root/"b"
    src.dirname().makedirs()
    src.write_text("a")
    def first(target, source):
        target.write_text(source.bytes() + "b")
    e = belt.Engine()
    belt.build(tgt, src, e)(first)
    e.run()
    t.eq(tgt.bytes(), "ab")

@t.root(t.base/"001"/"multi")
def test_multiple(root):
    tgt1, tgt2 = root/"a", root/"b"
    def first(target):
        target.write_text("a")
    def second(target, source):
        target.write_text(source.bytes() + "b")
    e = belt.Engine()
    belt.build(tgt1, e)(first)
    belt.build(tgt2, tgt1, e)(second)
    e.run()
    t.eq(tgt1.bytes(), "a")
    t.eq(tgt2.bytes(), "ab")