import urllib

from belt import build, glob, path

URL = "ftp://ftp.ncbi.nih.gov/genomes/Bacteria/lproks_1.txt"
BASE = path.getcwd()

@build(BASE/"lproks.txt")
def lproks(lproks):
    src = BASE/"lproks.input"
    src.copy(lproks)

@build(
    glob(BASE/"lp/*.lp"),
    BASE/"lproks.txt",
    BASE/"lproks.input",
)
def read_lproks(pattern, lptext, lpinput):
    with lptext.open() as handle:
        for i in range(2):
            handle.readline()
        for line in handle:
            bits = line.strip("\t\n").split("\t")
            newfn = BASE/("lp/%s-%s.lp" % (bits[0], bits[1]))
            if not newfn.dirname().exists():
                newfn.dirname().makedirs()
            newfn.write_bytes(line)

@build(BASE/"summary.txt", glob(BASE/"lp/*.lp"))
def summarize(summary, pattern):
    count = sum(map(lambda f: f.size, pattern.glob()))
    summary.write_text("Length: %s" % count)
