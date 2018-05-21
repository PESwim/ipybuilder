..  created on Fri Mar 24 17:26:26 2018
..  author: PE LLC peswin@mindspring.com
..  copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.
.. _Full Documentation:   https://peswim.github.io/ipybuilder/
.. _Examples:  https://peswim.github.io/ipybuilder/indxexplr.html
.. _gitzip:  https://github.com/PESwim/ipybuilder

.. |trade| unicode:: U+02122

**Apr 23, 2018 16:16 MST**

`Full Documentation`_

ipybuilder
==========

Command-line standalone IronPython™ 2.7.7 dll and exe file compiler. Uses, user
defined, assembly information, and input command args parsed by pseudo-ORDER. 

**Not Endorsed by C#.Net, IronPython, or Python**

Motivation and Development
--------------------------

Develop without Visual Studio\ |trade| - In an IronPython\ |trade| project I
ran into trouble distributing my project as the compiler code in "pyc.py" was
buggy, so I set out to fix it. 90% of the code is for the loose parameter input
format, error, and info output - that hopefully helps you complete a compile.

Use a command-line compile - shell .bat/.sh easily setup.

Intensionally verbose output - wanted users (me) to have extra-ordinary
feedback output and transparent coding, so that "hidden" 3rd party apps were
minimized. This is my first time public release. 

Use project as a general working reference for me/users/coders to see full
working complex code such as logging and unit testing.

While I'm not completely satisfied with the unit testing code, a lot of
other unit testing falls very short of completely testing a code base.
 
- **ipybuilder fixes several longtime running bugs in the IronPython**
  **pyc.py complier and then goes on to try and really help users build a**
  **project lib or exe.**

- **Please keep in mind this is alpha release for help/review**
  
- **Intensional: must keep out all** *non-IronPython* **available imports**
  
- **Intensionally kept imports to a minimum at the expense of re-writing the wheel.**
  **Wanted to be as transparent/independent as possible.**

Development System 
------------------
**ipybuild works for the author using Win7 64 bit python 32/64 with 
IronPython 2.7.7.1000** - thats the only test..so far.

Built Using
-----------
  - Developed in 32 bit Python 2.7.14
  - can't (do'nt know how) to use set.py for IronPython code
  - can't use pylint/enchant in 64 bit, so build with 32 bit
  - can't sphinx in 64 bit, so built with 32 bit
  
  check - should run in both ipy and python and 32/64bit 
  thats the only test so far....
 
Prerequisites Required
======================
- Microsoft\ |trade| .Net 4.0 - 4.6 framework
- IronPython\ |trade| 2.7.7.100
- Python\ |trade| 2.7.14 32 bit for documentation using pylint/enchant/sphinx

Installing
==========
  - git clone - :download: <https://github.com/PESwim/ipybuilder.git>
  - git zip install to "builder" directory:  `gitzip`_ 
  - download .zip - `ipybuilder.zip <underconstruciton>` 

Getting Started
===============
  - Project running on your local machine
    clone or unzip into ``builder`` directory
    
example runs
------------
`Examples`_

Documentation
=============
`Full Documentation`_

Running unit tests
==================

*todo tests run-through*

Contributing
============
Thanks for even considering a contribution or comment.

IMPORTANT: By submitting a patch, you agree to license your work under the
same license as that used by the project.

Keep it friendly and open to dialog critiques and fixes and to help beginners
and advanced users, while encouraging all levels of input.

Please work through what you can before asking for help - It is hard to get
relative paths and dependencies resolved when compiling an exe. Start small, 
work up to big.

If you are a first time GitHub contributor or beginner than I really encourage
you to submit a fix or comment, we both will learn. Of course Advanced help 
appreciated.

Want a solid easy way to Compile. The easier it is to use a program, the
more code work is required by developers. It really slows production down when you have to 
'on-line' search how to use a program module/library and/or fix bugs./patches.
Ultimately, hope ipybuilder can be a friendly bug-free command-line Compiler.

This is a free-time project so if my free-time goes away so does me ability to 
respond. Please be responsible with your comments and requests (see *Code of Conduct*). I hope you find
the answer/solution/explanation in the full-documentation.

****

coding style
------------
- *moderately verbose naming - no snake_case*

- *attempted goals*: 
  - Maximize readability and code comprehension
  - Minimize typing

*Some genius at Microsoft determined that PascalCase is the best.*    

*Some genius at Python determined that snake_case is the best.*

Trying to meet the following formats and let's try and avoid 
any discussion on appropriate style:

modules: lowercase
  \

classes: PascalCase
  - attributes:
  
    - internal: _camelCase
    - external: camelCase

methods:
  - checks, get, set, is etc.: camelCase      
  - internal: camelCase
  - external module to module imports or user available: PascalCase

variables:
  - local scope simple: short looping, internal, easily understood ("i","k", "dfpath", "dir")
  - intermodule or external inputs: camelCase verbose (long name) 
  - local scope complex:
    \
    - under ~ five-seven chars: lowercase
    - over ~ five-seven chars: camelCase
        \
constants/globals: uppercase
  \
pseudo constants: uppercase
  - logging setup, constant dict keys, and directories that are setup at runtime and derivatives.
    \
  - exception user config arg input variables**: **dict uses camelCase keys.
    \
:note:
    The whole point of this program is for working with python and C#.Net\ |trade|.
    When sub-classing a .net class it is much clearer to mirror a .Net class with a 
    python PascalClass name style to visually read code back and forth. 
    I really didn't focus on a consistent and standardized python-.Net naming style at the
    to start, as this package is only written in python. Now that I have worked out, what 
    seems to be a reasonable style, there are naming fixes that still need to be made this
    code. The naming style is relevant for all(my) other python-.net work. 
    
    Consider working in .net from the IronPython side and sub-classing (just an example)
    .net class System.IO.Directory. It is obvious what to expect(.net methods etc) with
    the PESwim style when reviewing, testing, and developing - not so much when you see 
    the snake_case form.
    
      Style type in IronPython (pseudo-code):
        - PESwim Style:
        .. code:: python
        
           class SystemIO(System.IO):
               pass  
           dirName = SystemIO.Directory.GetCurrentDirectory()  
             
        - snake_case Style:
        .. code:: python
        
           class system_io(System.IO):
               pass
           dirName = system_io.Directory.GetCurrentDirectory()   

work todo continues 
-------------------
*improve documentation - help - code comments - doc strings*
 \
*FAQ* 
 \
*on error bad arg parse may pollutes with multiple directory/file creates*
  Add del current writes/rmdirs on exit errors.
  
*add file_version info to dll files*
  Requires sub-classing IronPython CompileModules.
  
*clean out all globals except log*
  \
*separate unit tests from production code completely*
  Difficult, as wanted to test real-time run with subprocess, but
  have to run unit test from /Tests not /builder sub directory. This must 
  require lots of set-up mocks into a /builder like subdirectory so that 
  testing for 'Tests' in current working directory can be avoided in
  production code.
  
*adapt/try argparse*
  Trying out a structure free input style cost many hours and is about half
  the code-base. Also allowed non r"text" and both Unicode and str.
  Originally planned on complete structured free input so user doesn't have
  remember or learn an exact format. Found limits on how far this works and
  that eventually a main name has to be provided so no real use in accepting 
  command args that omit a main name.
  
*add a switch func to TerminalColorlog between windows and bash*
  Right now have to manually adjust the code.
  
*clean naming to match PascalCase throughout*
  The whole point of this program is for working with python and C#.net. When 
  sub-classing a .net class it is much clearer to mirror a .Net class with a 
  python PascalClase name style to visually read code back and forth. 
  I really didn't focus on naming to start as this package is only written
  in python, but is relevant for all my other work. Sorry.
 
*write a nice tutorial/how-to/steps*
 \
really kill anti-patterns and bad practice - life long pursuit - just started
-----------------------------------------------------------------------------
*adapt where possible parsing code that already exists*
  i.e. remove code that re-wrote the wheel.
   
*refactor if else into methods*
  Too many if else and multiple task methods - just takes a bit of time.
  
*wow these wonderful unit tests - what to do?* 
  \

known issues 
------------
- well none documented so far: Apr 23, 2018 16:51 MST

version issues v0.0.A20
-----------------------
  **Version v0.0.A20**
    - Second alpha release
    - Added Standalone ipybuilder.exe
    
  **Version v0.0.A10**
    - First alpha release
     
see section: work todo continues
  \

****

Versions
========
**v0.0.A20** - current
  May 18, 2018 01:08 MST
  
  **Version v0.0.A20**
    - ipybuilder.exe Standalone compiler
    - Alpha release to start
    - Tested:
      - Window 7 64 platform - 32 bit python
    - issues:
      see: issues v0.0.A20
      \  
  **Version v0.0.A10**
    - Alpha release to start
    - Tested:
      - Window 7 64 platform - 32 bit python
      
Authors
=======
Owner: Howard Dunn <peswin@mindspring.com>

Contributors
------------
- Please help by contributing

License
=======
ipybuilder is licensed under the Apache v2.0 License - see LICENSE file 
