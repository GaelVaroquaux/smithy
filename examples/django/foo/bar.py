
from belt import build

@build("bar.txt")
def mkbar(bar):
    bar.write_text("Hooray!")
