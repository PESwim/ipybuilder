# -*- coding: utf-8 -*-
"""
.. created on Sun Mar 18 02:26:52 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""

clr = None
try:
    import sys
    import clr
    # need System if "using" System for/as net type implementation
    clr.AddReference("System") #no fail if .netframework 4.0+
    import System
except Exception as exs:
    pass

try:# if you are not standalone catch (do not need if you know)
    clr.AddReference("IronPython")
    import IronPython
except Exception as exc:
    if clr:
        print('"IronPython" not availible as AddReference') # reminds you

if clr:
    try:
        clr.AddReference("ipybuild")
    except System.IO.IOException as ex:
        if clr:
            print('ipybuild reference error:\n\t' + \
                  'check file | filepath')    
import version   
from version import __version__
import os

class GlobalState(object):
    '''
      #TODO trying to clean up globals
      currently only used for the *required* module
      
      **gsBuild**: Global class holding required paths and existence
      information when the install IronPython path is/is not found.
    
    '''
    
    def __init__(self):
        pass

gsBuild = GlobalState()
gsBuild.Verbose = False
gsBuild.INFO = True

if any('-v' in arg for arg in sys.argv):
    sys.argv.remove('-v')
    gsBuild.Verbose = True
    gsBuild.INFO = True
    print('\ncur wrk dir - {}'.format(os.getcwd()))
    print('\n"IF" error: check "all" paths absolute or relative' + \
          ' to "ipybuild" run directory.\n')

if __name__ == '__main__':    
    pass
