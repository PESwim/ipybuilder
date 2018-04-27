# -*- coding: utf-8 -*-
"""
.. created on Tue May 01 17:25:41 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""

clr = None
try:
    import clr
    clr.AddReference("System")
    import System
except Exception:
    pass

from version import __version__
import sys
import os
from os import path as op
from os.path import abspath as opabs
from os.path import exists as opex
from os.path import join as opj
from os.path import normpath as opn
from os.path import dirname as opd
from os.path import basename as opb
from os.path import relpath as oprel
from buildlogs import dynfile
from globalstate import gsBuild
import subprocess
from subprocess import PIPE

log = dynfile(__name__)
log.debug('\n---------------- ' + str(__name__) + \
              ' loaded --------------------')

def cleanDll():
    
    try:
        cleandlls = gsBuild.DELDLLS
    except Exception as exd:
            print 'No Cleanup'
            print(exd)
    if cleandlls:
        cleanedDlls = list(cleandlls)        
        for cleandll in cleandlls:
            if opex(cleandll):   
                try:
                    os.remove(cleandll)
                    cleanedDlls.remove(cleandll)
                except Exception as ex:
                    log.warn(str(ex))
            else:
                cleanedDlls.remove(cleandll)
                log.error('\n No reason to cleanup {}.'.format(cleandll))
                
    if cleanedDlls:
        for dll in cleanedDlls:
            delCmd = ['cmd /c del '] + [dll]    
            try:
                subprocess.check_output(delCmd)
            except Exception as exd:
                log.warn("\nCan't cleanup in ipybuilder {}".format(cleandll))

if __name__ == '__main__':
    pass