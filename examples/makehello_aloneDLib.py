"""
.. created on Mon Mar 12 22:14:23 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""
# THIS IS THE EMBEDED EXAMPLE- The .exe file has two embeded resources
# - a blob IPDLL file which handles the ipy and sys overhead to start
# - a blob DLL.project + DLL resources holding all the user libs 
#    * for this example those are the make.py, ipyver.py --> to dll files*
#    * this internal resource is auto-name makehello_embedDLL *
#    *requires the main.py --> main.exe file to add the mainDLL to the clr*
#    i.e.  ``clr.AddReference("makehello_embedDLL")``

# IronPython must still be installed along with the .net Framework to run .exe


# FIRST - get path to a Ironpython Lib for simple exe
# You need this for any imports except sys and the ipy builtins

import sys
#sys.path.append('../../../../ironpython/Lib') #Works on my devop machine
# if you use the sys.path method you cant move the exe file/dlls into a path
# that can not find the python Lib files.

# NOTE: If you have ipy installed and test this file without the path it WILL work.
# that is because ipy install sets a global path, but once you compile the exe version
# can no longer acces the global path. This makes it possible to have a standalone
# that works, as otherwise the paths a hard coded into exe compiled file.
 
# *OR* works anywhere you have path to stdlib

import clr # must have IronPython installed
clr.AddReference('StdLib')

# Now we have acces to std imports
import os
# We need System for this Example
try:
    import System
    from System import IO
except Exception as exi:
    print('IOEX ', str(exi))

import time    
print "see clr refs"
print clr.References
print 'Time'
print time.ctime()

def main():

    print('CurrentDirectory:\n {}'.format(System.IO.Directory.GetCurrentDirectory()))
    # we need the dll libraries we added to the dll list to run the following
    # Becasue they are embeded we load the auto-named internally embedded lib
    # mainname + DLL to get acces to the internal resources
    #
    # *OR* if you add the dendency files ipyver.py and make.py to the listexe
    # then you will not have a projectDLL and will not have to AddRef.
    # This only works if you have dependancies in .py format
    #
    # TODO the other way is to merge the stub .dll with the user lib .dll, 
    # I don't know how to do that yet.

    clr.AddReference("makehello_aloneDLibDLL")
    import make
    import ipyver
    import inspect

    sysfile = System.__file__.split(',')
    System.Console.WriteLine(('HAVE SYSTEM:\n' + '{}\n'*len(sysfile)) \
                              .format(*sysfile))
    print
    print "clr refs"
    print clr.References
    print
    print 'library imports'
    for md in sys.modules:
        if md.find('make') != -1 or md.find('ipyv') != -1:
            print(md)
    print
    rsp = ipyver.ReferenceStatus('inspect').RefStatus()
    for k, v in rsp.iteritems():
        print('inspect {}:{}'.format(k,v))   

    print     
    print('make dll from: {}'.format(inspect.getfile(make)))
    print('from make.hello - should get >>> "hello"')
    make.hello()

    print
    from make import hello
    print('from make import hello - should get >>> "hello"')
    hello()

if __name__ == '__main__':
    main()