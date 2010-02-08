Trawl - Another tool in the shed
================================

This is as straight of a clone of Rake that I could come up with.

Briefly:
::

    # Trawlfile
    @task
    def bar():
        print "BAR!"

Does as you might expect:
::

    $ trawl -T
    bar
    $ trawl bar
    ** Execute bar
    BAR

And with dependencies:
::

    # Trawlfile
    @task
    def bar():
        print "BAR!"

    @task([bar])
    def foo():
        print "FOO!"

Also does what you'd expect:
::

    $ trawl -T
    bar
    foo
    $ trawl bar
    ** Execute bar
    BAR!
    $ trawl foo
    ** Execute bar
    BAR!
    ** Execute foo
    FOO!

Which is awesome sauce, but what about files?
::

    # Trawlfile
    @build("myfile.txt", recreate=False)
    def run(task):
        with open(task.name) as out:
            out.write("MUNCTIONAL!")

    @build("yup.cfg", ["myfile.txt"])
    def more(task):
        with open(task.name) as out:
            with open(task.source) as src:
                out.write(src.read() + "!!!1!")

Will cause "myfile.txt" to be created but not overwritten if it exists.
"yup.cfg" will then only be rebuilt when "myfile.txt" changes as determined by
the file's mtime:
::

    $ trawl yup.cfg
    ** Execute myfile.txt
    ** Execute yup.cfg
    $ trawl yup.cfg
    $

The last major bit is in defining rules:
::

    @rule('.o', '.c'):
    def compile(task):
        subprocess.check_call(["gcc", "-o", task.name, "-c", task.source])
        
    objects = FileList("*.c").sub(".c$", ".o")
    @build("appname", objects)
    def link(task):
        subprocess.check_call(["gcc", "-o", task.name] + task.sources)

    # Add a helpful handle for running
    task("run", ["appname"])

TODO
++++

Some things that need to be done yet:

* Task descriptions
* Argument support
* Test and add methods to FileList
* Add a function to import tasks programatically

