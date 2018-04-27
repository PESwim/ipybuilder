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

# reminds you
if clr:

    try:# if you are not standalone catch (do not need if you know)
        clr.AddReference("IronPython")
        import IronPython
    except Exception as exc:
        print('"IronPython" not availible as AddReference') 

    f_ipy = False
    try:
        import ipyver
        rs = ipyver.ReferenceStatus()
        f_ipy = rs.RefStatusIPMS()['ipy']['isLocal']
    except System.IO.IOException as ex:
        pass
    
    try:
        clr.AddReference("ipybuild")
    except System.IO.IOException as ex:
        try:
            clr.AddReference("ipybuilder")
        except System.IO.IOException as ex:
            if f_ipy:
                print('IF .exe: ipybuild(er) reference error:\n\t' + \
                      'check file | filepath')

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
        
        self.Verbose = False
        self.INFO = True #set false for debug
        self.IPATH = None
        self.IPYBLDPATH = None
        self.DELDLLS = None

gsBuild = GlobalState()
gsBuild.Verbose = False
gsBuild.INFO = True #set false for debug
gsBuild.IPATH = None
gsBuild.IPYBLDPATH = sys.argv[0]
gsBuild.OK = False

if any('-v' in arg for arg in sys.argv):
    sys.argv.remove('-v')
    gsBuild.Verbose = True
    gsBuild.INFO = True #set False for debug
    print('\ncur wrk dir - {}'.format(os.getcwd()))
    print('\n"IF" error: check "all" paths absolute or relative' + \
          ' to "ipybuild" run directory.\n')

if __name__ == '__main__':
    pass
