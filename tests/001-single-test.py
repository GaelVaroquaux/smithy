
import t
import belt

@t.root(t.base/"001"/"simple")
def test_simple(root):
    tgt = root/"a"
    def first(target):
        target.write_text("a")
    e = belt.Engine()
    e.add(first, [], [tgt])
    e.run()
    t.eq(tgt.bytes(), "a")

@t.root(t.base/"001"/"multi")
def test_multiple(root):
    tgt1 = root/"multiple.1"
    tgt2 = root/"multiple.2"
    def first(target):
        target.write_text("a")
    def second(target, source):
        target.write_text(source.bytes() + "b")
    e = belt.Engine()
    e.add(first, [], [tgt1])
    e.add(second, [tgt1], [tgt2])
    e.run()
    t.eq(tgt1.bytes(), "a")
    t.eq(tgt2.bytes(), "ab")