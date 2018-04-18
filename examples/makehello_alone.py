"""
.. created on Tue Apr 17 23:56:05 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""

import clr
clr.AddReference("System")
import System
from System import IO
def main():
    
    print('CurrentDirectory ', IO.Directory.GetCurrentDirectory())
    
    try:
        clr.AddReference("StdLib")
    except System.IO.IOException as ex:
        print('IOEX ',ex.Message)

    sysfile = System.__file__.split(',')
    System.Console.WriteLine(('HAVE SYSTEM:\n' + '{}\n'*len(sysfile)) \
                              .format(*sysfile))
    import ipyver
    from ipyver import ReferenceStatus
    import inspect
    import make
    
    rsp = ReferenceStatus('inspect').RefStatus()
    for k, v in rsp.iteritems():
        print('inspect {}:{}'.format(k,v))   
    
    rsi = ReferenceStatus('ipyver').RefStatus()
    for k, v in rsi.iteritems():
        print('ipyver {}:{}'.format(k,v))   
        
    print('make dll from: {}'.format(inspect.getfile(make)))
    print('from make.hello - should get >>> "hello"')
    make.hello()

    from make import hello
    print('from make import hello - should get >>> "hello"')
    hello()

if __name__ == '__main__':
    main()