# Copyright 2010 Paul J. Davis <paul.joseph.davis@gmail.com>
#
# This file is part of the Smithy package released under the MIT license.

import t

@t.filetest
def test_create_empty():
    t.eq(len(t.FileList()), 0)

@t.filetest
def test_create_with_args():
    fl = t.FileList("*.c", "x")
    t.eq(sorted("abc.c x.c xyz.c x".split()), sorted(fl))

@t.filetest
def test_str():
    fl = t.FileList("a.c", "b.c", "x.py")
    t.eq(str(fl), "[a.c, b.c, x.py]")
    t.eq("%s" % fl, "[a.c, b.c, x.py]")

@t.filetest
def test_str_resolve():
    fl = t.FileList("*.c")
    str(fl)
    t.eq(len(fl), 3)

@t.filetest
def test_delayed_resolve():
    # Check sanity
    fl = t.FileList("*.c")
    t.eq(len(fl), 3)
    
    # Check basic delay
    fl = t.FileList("*.c")
    t.eq(len(fl._items), 0)
    str(fl)
    t.eq(len(fl._items), 3)
    
    # Check trigger by second reference
    fl = t.FileList("*.c")
    t.eq(len(fl._items), 0)
    fl2 = fl
    t.eq(len(fl._items), 0)
    t.eq(len(fl._items), 0)
    repr(fl2)
    t.eq(len(fl._items), 3)
    t.eq(len(fl._items), 3)
    
    # Check after copy
    fl = t.FileList("*.c")
    t.eq(len(fl._items), 0)
    fl2 = fl.copy()
    t.eq(len(fl._items), 0)
    t.eq(len(fl2._items), 0)
    repr(fl2)
    t.eq(len(fl._items), 0)
    t.eq(len(fl2._items), 3)

    # Check expand doesn't affect the original
    fl3 = fl.expand()
    t.eq(len(fl._items), 0)
    t.eq(len(fl3._items), 3)
    t.eq(fl2 == fl3, True)

@t.filetest
def test_reresolve():
    fl = t.FileList("a.c", "*.c")
    for i in range(10):
        fl.resolve()
        t.eq(len(fl), 4)

@t.filetest
def test_create_from_iterable():
    fl = t.FileList(["x", "y", "z"])
    t.eq(sorted(fl), sorted(["x", "y", "z"]))

@t.filetest
def test_include_other_file_list():
    fl = t.FileList(t.FileList("*.c", "x"))
    t.eq(sorted(fl), sorted(["abc.c", "x.c", "xyz.c", "x"]))

@t.filetest
def test_append():
    fl = t.FileList()
    fl.append("a.py")
    fl.append("b.py")
    t.eq(fl, ["a.py", "b.py"])

@t.filetest
def test_add_many():
    fl = t.FileList()
    fl.include("a x c".split())
    fl.include("d", "y")
    t.eq(sorted(fl), "a c d x y".split())

@t.filetest
def test_match():
    fl = t.FileList()
    fl.include("*.c")
    t.isin("abc.c", fl)
    t.eq(len(fl), 3)
    map(lambda p: t.eq(p.ext, ".c"), fl)

@t.filetest
def test_add_matching():
    fl = t.FileList()
    fl.append("a.java")
    fl.include("*.c")
    t.eq(fl[0], "a.java")
    t.eq(len(fl), 4)
    t.isin("abc.c", fl)

@t.filetest
def test_multiple_patterns():
    fl = t.FileList("foo/*.c", "bar/*xist*")
    t.eq(fl, [])
    fl.include("*.c", "*xist*")
    t.eq(sorted(fl), sorted("abc.c existing x.c xyz.c".split()))

@t.filetest
def test_square_bracket_pattern():
    fl = t.FileList("abc.[ch]")
    t.eq(sorted(fl), ["abc.c", "abc.h"])

@t.filetest
def test_filter():
    fl = t.FileList()
    fl.include("x.c abc.c xyz.c existing".split())
    fl = filter(lambda p: "x" not in p, fl)
    t.eq(sorted(fl), ["abc.c"])

@t.filetest
def test_exclude():
    fl = t.FileList("x.c", "abc.c", "xyz.c", "existing")
    x = fl.exclude_re(r"x.+\.")
    t.isinstance(x, t.FileList)
    t.eq(sorted(fl), ["abc.c", "existing", "x.c"])
    t.eq(id(fl), id(x))
    fl.exclude("*.c")
    t.eq(fl, ["existing"])
    fl.exclude("existing")
    t.eq(fl, [])

@t.filetest
def test_exclude_via_callable():
    fl = t.FileList("a.c", "b.c", "xyz.c")
    fl.exclude(lambda x: x == "xyz.c")
    t.eq(fl, ["a.c", "b.c"])

@t.filetest
def test_exclude_re():
    fl = t.FileList("*").exclude_re(r".*\.[hcx]$")
    t.eq(sorted(fl), ["existing", "x"])
    t.isinstance(fl, t.FileList)

@t.filetest
def test_exclude_filename():
    fl = t.FileList("*.c").exclude("abc.c")
    t.eq(sorted(fl), ["x.c", "xyz.c"])
    t.isinstance(fl, t.FileList)

@t.filetest
def test_default_excludes():
    fl = t.FileList()
    fl.clear_excludes()
    fl.include("*~", "*.bak", "core")
    t.isin("core", fl)
    t.isin("x.bak", fl)
    t.isin("x~", fl)

@t.filetest
def test_clear_excludes():
    fl = t.FileList("*")
    t.isnotin("CVS", fl)
    t.isnotin(".svn", fl)
    t.isnotin(".dummy", fl)
    t.isnotin("x.bak", fl)
    t.isnotin("x~", fl)
    t.isnotin("core", fl)    

@t.filetest
def test_exclude_alternate_file_seps():
    fl = t.FileList()
    t.eq(fl.is_excluded("x/CVS/y"), True)
    t.eq(fl.is_excluded("x\\CVS\\y"), True)
    t.eq(fl.is_excluded("x/.svn/y"), True)
    t.eq(fl.is_excluded("x\\.svn\\y"), True)
    t.eq(fl.is_excluded("x/.git/y"), True)
    t.eq(fl.is_excluded("x\\.git\\y"), True)
    t.eq(fl.is_excluded("x/core"), True)
    t.eq(fl.is_excluded("x\\core"), True)

    # Core as path component is kosher.
    t.eq(fl.is_excluded("x/core/y"), False)
    t.eq(fl.is_excluded("x\\core\\y"), False)

@t.filetest
def test_add_to_exclude():
    fl = t.FileList()
    fl.exclude_re(r"~\d+")
    t.eq(fl.is_excluded("x/CVS/y"), True)
    t.eq(fl.is_excluded("x\\.git\\y"), True)
    t.eq(fl.is_excluded("x/core"), True)
    t.eq(fl.is_excluded("abc~3"), True)

@t.filetest
def test_sub():
    fl = t.FileList("*.c")
    fl.sub(r".c$", ".o")
    t.eq(sorted(fl), ["abc.o", "x.o", "xyz.o"])

@t.filetest
def test_sub_with_backref():
    fl = t.FileList("src/org/onestepback/a.java", "src/org/onestepback/b.java")
    fl.sub(r"^src/(.*).java$", r"classes/\1.class")
    t.eq(sorted(fl), [
        "classes/org/onestepback/a.class",
        "classes/org/onestepback/b.class"
    ])

@t.filetest
def test_exist():
    fl = t.FileList("abc.c", "notthere.c")
    t.eq(fl.exist(), ["abc.c"])

@t.filetest
def test_doesnt_subclass_list():
    fl = t.FileList("*.c")
    t.eq(isinstance(fl, list), False)

@t.filetest
def test_not_hashable():
    fl = t.FileList("*.c")
    t.raises(TypeError, hash, fl)

@t.filetest
def test_add_arrays():
    t.eq(t.FileList("a.c", "b.c") + ["foo.py"], ["a.c", "b.c", "foo.py"])
    t.eq(["foo.py"] + t.FileList("a.c", "b.c"), ["foo.py", "a.c", "b.c"])
    t.raises(TypeError, lambda: t.FileList("a.c", "b.c") + 1)
    t.raises(TypeError, lambda: t.FileList("a.c", "b.c") + [1])
    t.raises(TypeError, lambda: 1 + t.FileList("a.c", "b.c"))
    t.raises(TypeError, lambda: [1] + t.FileList("a.c", "b.c"))

@t.filetest
def test_length():
    t.eq(len(t.FileList("a.c", "b.c")), 2)
    t.eq(len(t.FileList("*.c")), 3)

@t.filetest
def test_iter():
    fl = t.FileList("a.c", "b.c", "exist*")
    i = iter(fl)
    t.eq(isinstance(i, t.FileListIter), True)
    t.eq(i.next(), "a.c")
    t.eq(isinstance(i.next(), t.path), True)
    t.eq(i.next(), "existing")
    t.raises(StopIteration, i.next)

@t.filetest
def test_get_item():
    fl = t.FileList("a.c", "b.c")
    t.eq(fl[0], "a.c")
    t.eq(fl[-1], "b.c")
    t.raises(IndexError, lambda: fl[100])

@t.filetest
def test_set_item():
    fl = t.FileList("a.c", "b.c")
    fl[0] = "foo.py"
    t.eq(fl, ["foo.py", "b.c"])
    def assign():
        fl[1] = 2
    t.raises(TypeError, assign)

@t.filetest
def test_del_item():
    fl = t.FileList("a.c", "b.c")
    del fl[0]
    t.eq(fl[0], "b.c")
    def rem():
        del fl[2]
    t.raises(IndexError, rem)

@t.filetest
def test_contains():
    fl = t.FileList("*.c")
    t.isin("abc.c", fl)
    t.isin("x.c", fl)
    t.isin("xyz.c", fl)

@t.filetest
def test_get_slice():
    fl = t.FileList("a.c", "b.c", "exist*")
    fl1 = fl[1:]
    t.eq(fl1, ["b.c", "existing"])
    t.eq(isinstance(fl1, t.FileList), True)

@t.filetest
def test_set_slice():
    fl1 = t.FileList("a.c", "b.c", "exist*")
    fl2 = t.FileList("d.c")
    fl1[1:2] = fl2
    t.eq(fl1, ["a.c", "d.c", "existing"])
    fl1[2:] = ["d.e"]
    t.eq(fl1, ["a.c", "d.c", "d.e"])

@t.filetest
def test_del_slice():
    fl = t.FileList("a.c", "b.c", "exist*")
    del fl[1:]
    t.eq(fl, ["a.c"])

@t.filetest
def test_comparisons():
    fl1 = t.FileList("a.c", "exist*")
    fl2 = t.FileList("b.c")
    fl3 = t.FileList("a.c", "exist*")

    # __lt__
    t.eq(fl1 < fl2, True)
    t.eq(fl2 < fl1, False)
    t.eq(fl1 < ["d.e"], True)
    t.eq(["a.c"] < fl2, True)
    t.eq(["z.x"] < fl1, False)

    # __le__
    t.eq(fl1 <= fl1, True)
    t.eq(fl1 <= fl2, True)
    t.eq(fl2 <= fl1, False)
    t.eq(fl1 <= ["d.e"], True)
    t.eq(["_"] <= fl1, True)
    t.eq(["z.c"] <= fl2, False)
    
    # __eq__
    t.eq(fl1 == fl3, True)
    t.eq(fl3 == fl1, True)
    t.eq(fl2 == fl2, True)
    t.eq(fl2 == ["b.c"], True)
    t.eq(fl1 == fl2, False)
    t.eq(fl1 == ["z"], False)
    t.eq(["b.c"] == fl2, True)
    t.eq(["z"] == fl1, False)
    
    # __ne__
    t.eq(fl1 != fl2, True)
    t.eq(fl1 != fl1, False)
    t.eq(fl1 != fl3, False)
    t.eq(fl1 != ["a.c", "existing"], False)
    t.eq(fl2 != fl3, True)
    t.eq(["z.b"] != fl2, True)
    t.eq(["a.c", "existing"] != fl1, False)
    
    # __ge__
    t.eq(fl1 >= fl3, True)
    t.eq(fl2 >= fl1, True)
    t.eq(fl1 >= fl2, False)
    t.eq(fl1 >= ["_"], True)
    t.eq(fl2 >= ["z.c"], False)
    t.eq(["z.c"] >= fl2, True)
    t.eq(["b.c"] >= fl2, True)
    t.eq(["a"] >= fl1, False)
    
    # __gt__
    t.eq(fl2 > fl1, True)
    t.eq(fl1 > fl2, False)
    t.eq(fl2 > ["a.c"], True)
    t.eq(fl2 > ["z.c"], False)
    t.eq(["z.c"] > fl1, True)
    t.eq(["a"] > fl3, False)
