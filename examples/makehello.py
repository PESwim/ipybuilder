"""
.. created on Mon Mar 12 22:14:23 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""

import clr
import System
import sys
sys.path.append('../../../builder')
sys.path.append('../../../ironpython/Lib')
try:    
    from ipyver import ReferenceStatus
except ImportError as ex:
    print('Should Error if dir "/Builder" not in path for "ipyver"' )
    raise ex
    
def main():
    clr.AddReference("System")
    from System import IO
    print('CurrentDirectory:\n '.format(IO.Directory.GetCurrentDirectory()))
    
    try:
        clr.AddReference("make")
    except System.IO.IOException as ex:
        print('IOEX ',ex.Message)
    try:
        clr.AddReference("StdLib")
    except System.IO.IOException as ex:
        print('IOEX ',ex.Message)
        
    sysfile = System.__file__.split(',')
    System.Console.WriteLine(('HAVE SYSTEM:\n' + '{}\n'*len(sysfile)) \
                              .format(*sysfile))

    import inspect
    import make
    
    rsp = ReferenceStatus('inspect').RefStatus()
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