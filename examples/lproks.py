import urllib
import belt as b

URL = "ftp://ftp.ncbi.nih.gov/genomes/Bacteria/lproks_1.txt"
BASE = b.path.getcwd()

@b.files(None, BASE/"lproks.txt")
def lproks(job, src, tgt):
    data = urllib.urlopen(URL).read()
    tgt.write_bytes(data)

@b.files(BASE/"lproks.txt", None)
def read_lproks(job, src, tgt):
    with src.open() as handle:
        for i in range(2):
            handle.readline()
        for line in handle:
            bits = line.strip("\t\n").split("\t")
            newfn = BASE/"%s-%s.lp" % (bits[0], bits[1])
            newfn.write_bytes(line)
            j.add_file(newfn)

@b.files(read_lproks, BASE/"summary.txt")
def summarize(job, srcs, tgt):
    sum = 0
    for src in srcs:
        sum += len(src.bytes())
    tgt.text("Length: %s" % num_bytes)
