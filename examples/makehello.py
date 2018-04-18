"""
.. created on Mon Mar 12 22:14:23 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""


# FIRST - get path to a Ironpython Lib for simple exe
import sys
#sys.path.append('../../../../ironpython/Lib') #Works on my devop machine
# if you use the sys.path method you cant move the exe file/dlls into a path
# that can not find the python Lib files.

# NOTE: If you have ipy installed and test this file without the path it WILL work.
# that is because ipy install set a global path, but once you compile the exe ver
# can no longer acces the global path. This makes it possible to have a standalone
# that works.
 
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
    
print "see clr refs"
print clr.References
 
def main():

    print('CurrentDirectory:\n '.format(System.IO.Directory.GetCurrentDirectory()))
    # we need the dll libraries we add to the dll list to run the following
    try:
        clr.AddReference("make")
        clr.AddReference("ipyver")
    except System.IO.IOException as ex:
        print('IOEX ',ex.Message)
        
    sysfile = System.__file__.split(',')
    System.Console.WriteLine(('HAVE SYSTEM:\n' + '{}\n'*len(sysfile)) \
                              .format(*sysfile))
    
    try:
        import ipyver  #from iypver.dll
        import inspect #from stdlib or ipy sys.path
        import make    #from make lib
    except Exception as ex:
        print('err on import')
        print(ex)
        
    rsp = ipyver.ReferenceStatus('inspect').RefStatus()
    for k, v in rsp.iteritems():
        print('inspect {}:{}'.format(k,v))   
    
    print('make dll from: {}'.format(inspect.getfile(make)))
    print('from make.hello - should get >>> "hello"')
    make.hello()

    from make import hello
    print('from make import hello - should get >>> "hello"')
    hello()

if __name__ == '__main__':
    main()