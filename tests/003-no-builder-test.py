
import t
import belt

@t.root(t.base/"003"/"no-source")
def test_no_source(root):
    src, tgt = root/"s", root/"t"
    if src.exists():
        src.remove()
    def first(tgt, src):
        tgt.write_bytes("a")
    e = belt.Engine()
    belt.build(tgt, src, e)(first)
    t.raises(RuntimeError, e.run)
    t.eq(tgt.exists(), False)

@t.root(t.base/"003"/"missing-source")
def test_missing_source(root):
    src, mid, tgt = root/"s", root/"m", root/"t"
    def first(tgt):
        tgt.write_bytes("a")
    def second(tgt, src):
        tgt.write_bytes("a")
    e = belt.Engine()
    belt.build(src, e)(first)
    belt.build(tgt, mid, e)(second)
    t.raises(RuntimeError, e.run)
    if src.exists():
        # Might've evaulated missing mid first.
        t.eq(src.bytes(), "a")
