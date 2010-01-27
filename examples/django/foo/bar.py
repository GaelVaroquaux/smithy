
import belt as b

@b.build("bar.txt")
def mkbar(bar):
    bar.write_text("Hooray!")
