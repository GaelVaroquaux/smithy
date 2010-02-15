Overview
========

Smithy is a Python port of `Rake <http://rake.rubyforge.org/>`_. While it currently has a compatible core set of features, some of the extra fancy bits have not yet been worked on. If you would like to see your favorite Rake feature added feel free to open an issue on `GitHub <http://github.com/davisp/smithy/>`_ or better yet, send me a pull request.

You can find the source code repository at `http://github.com/davisp/smithy <http://github.com/davisp/smithy>`_.

Smithy is released under the `MIT license <license.html>`_.

Installation
============

Via ``easy_install``::

    $ easy_install smithy==dev

Or from a source checkout::

    $ git clone git://github.com/davisp/smithy.git
    $ cd smithy
    $ python setup.py test
    $ sudo python setup.py install

Note that you can also use ``sudo python setup.py develop`` to be able to modify the code in place without the need to reinstall. This is helpful for testing patches.


A Simple Example
================

Once installed, you'll run the ``smithy`` command to execute your defined tasks:
::

    $ smithy [OPTIONS] task1 [task2 ...]

You can use ``smithy -h`` to see the complete list of options.

Given a ``Bellows`` file that looks like such:
::

    @task
    def prereq():
        print "I am a prereq"
    
    @task([prereq])
    def test():
        print "I have been tested!"

Running smithy from the directory containing this ``Bellows`` file should look like this::

    $ ls
    Bellows
    $ smithy test
    ** Execute prereq
    I am a prereq
    ** Execute test
    I have been tested!

Smithy is on your side.

Bellows File Format as of (0.2.0)
=================================

As in Rake, Bellows files are actually arbitrary Python scripts. Smithy merely presents these scripts with a few methods and decorators for declaring tasks.

Tasks
+++++

The most basic unit of work in a Bellows file is a task. A task has a type, a name, an action and a set of dependencies. Only type and name are required. Task type's are generally implicit and decided by how the task was declared.

Tasks definitions are cumulative. If a task is defined multiple times, its definitions are joined into a single task definition that is treated as a single entity. This allows you to progressively build up tasks as you see fit.

Basic Tasks
-----------

A basic task just declares that the task exists. Its not hugely exciting.

::

    task("name")

Declaring Dependencies
----------------------

Tasks can have dependencies. Dependencies must be passed as an array or tuple. This is required to disambiguate possible parameter combinations as will be discussed below.

::

    task("name", ["dependency1", "dependency2"])

Tasks don't need to exist before they're referenced in a dependency list. If the ``name`` task is being processed and there still isn't an available task for one of it's dependencies an error is reported and execution is aborted. Task are never run until after all files defining tasks have been read.

Tasks with Actions
------------------

Just declaring tasks doesn't really do much for us. Adding actions to tasks is where things start to take shape.

::

    @task("mytask")
    def run():
        print "This is my task!"

As you can see, we can use the ``task`` function as a decorator. In this case the task will be named ``mytask`` and will print an informative message when it is run.

Dependencies also work as expected:
::

    @task("mytask", ["yourtask"])
    def run():
        print "Your task will run before my task."

Here we've declared a depenency on ``yourtask`` which will run before an attempt is made to run ``mytask``.

Task Arguments
--------------

If you define a task action that accepts a single parameter, the Task object will be passed to the action. This can help if a function is reused for multiple actions. The task argument is also helpful when working with Rules.
::

    @task("happytask", ["foo", "bar"])
    def mytask(t):
        print "%s depends on %s" % (t.name, ', '.join(t.sources))

Would print ``'happy_task depends on foo, bar'``.

Auto-Imported Functions from Smithy
-----------------------------------

When a task definition file is loaded by smithy, the commonly used functions are automatically inserted into the global scope. This means that you are not required to explicitly import anything from smithy for basic operation. This is the complete list of symbols that are available:

* __file__ - The filename that is being executed.
* FileList - The FileList class for dealing with lists of file names.
* require - Loading other task files.
* task - Our friendly task function.
* rule - Define a rule to create implicit tasks for unmet dependencies
* build - Define a task that creates a file.
* multitask - Not yet implemented.
* ns - Used in with-statements to help avoid task name clobbering.

The unfamiliar symbols will be described in further detail below.

Task Names from Functions
-------------------------

It's a bit silly to require that we name a task when there's a perfectly acceptable function name right there. And as such the task name is not required to be explicitly specified. If the first parameter to ``task`` is omitted it will use the function name:
::

    @task
    def run():
        "This task is named 'run'."

And adding dependencies still works as expected:
::

    @task(["yourtask"])
    def run():
        "This task will still run after 'yourtask'"

.. warning::

 Notice that if we didn't require dependencies to be specified as a list (or tuple) then when we borrow the name of the function we would be unable to determine if the first argument is a task name or a dependency. I'm not really fond of ambiguity and the syntax is the best compromise I could come up with.

 If you can think of something better, please don't hesitate to open a new issue describing it.

Repeated Definitions
--------------------

As mentioned earlier, multiple task definitions are combined. This allows you to define task actions and dependencies in separate locations.
::

    task("name")
    task("name", ["dependency1"])
    task("name", ["dependency2"])
    @task
    def name():
        print "My task!"

File Tasks
----------

File tasks are defined with the ``build`` function. I would've used file but that would clash with the built-in method.

File tasks require that the first parameter specifying a file name is present:
::

    @build("myfile.txt")
    def buildfile():
        with open("myfile.txt", "w") as out:
            out.write("Hi, mom!")

File tasks can have dependencies as well:
::

    @build("myfile.txt", ["otherfile.txt"])
    def buildfile():
        with open("myfile.txt", "w") as out:
            out.write("Hi, mom!")

If all of a file task's dependencies are also file tasks, and the time stamp for each of the dependent files is less than the time stamp on the file being built, the task is not run.

File Creation Tasks
-------------------

You can specify that file tasks will not run if their target file name already exists regardless of dependencies:
::

    @build("myfile.txt", recreate=False)
    def buildfile():
        with open("myfile.txt", "w") as out:
            out.write("Hi, mom!")

This task will only run when ``myfile.txt`` does not exist.

Namespaces
----------

To help avoid task name clashes, you can use namespaces to separate task definitions:
::

    with ns("foo"):
        
        @task
        def mytask():
            print "this is foo:mytask"
        
        with ns("bar"):
            
            @task
            def mytask():
                print "This is foo:bar:mytask"

As can be seen, namespaces can be nested arbitrarily.

There's also an alternative syntax to combine namespace nesting to help avoid unnecessarily indentation:
::

    with ns("foo", "bar"):
        
        @task
        def mytask():
            print "This is foo:bar:mytask"

Rules
-----

Some times we don't necessarily know what file names will be necessary but we can define rules for creating tasks to build the required files. The traditional compiling of a "Hello, World!" application might look something like:
::

    import subprocess as sp
    
    @rule('.o', '.c')
    def compile(t):
        # t.source refers to the first element of the sources array
        sp.check_call(['gcc', '-o', t.name, t.source])
    
    @build("awesome_app", ['obj1.o', 'obj2.o'])
    def link(t):
        sp.check_call(['gcc', '-o', t.name] + t.sources)
    
Implicit File Tasks
-------------------

Each time Smithy goes to execute a task it will try and resolve the task dependencies and if need be, execute them. When Smithy finds a task dependency for which there is no definition, it does one of two things:

1. Apply any rules that match the task name.
2. Attempt to make a file task that is a no-op task.

This way you can refer to files on the file system as dependencies. They will be evaluated for time stamp ordering and so on, but no action will ever be executed on their behalf.

Requiring other Task Files
==========================

If you want, you can load other task definition files from the main Bellows file. Files that are loaded are not actually processed until the current file is finished being evaluated. Requiring a file is as simple as:
::

    require("my_other_file.py")
    
The file name is completely arbitrary as long as it exists.

Feedback
========

Development is still quite young on this project. I'm using it as I develop it so I have a pretty good motivation to keep it on track. If you have suggestions or want to contribute find me as ``davisp`` on `irc.freenode.net <http://freenode.net>`_ or as `davisp on GitHub <http://github.com/davisp>`_.
