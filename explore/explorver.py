# -*- coding: utf-8 -*-
"""
.. created on Tue Apr 10 00:05:06 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

   *Example use of ipyver*
   
"""
import os
import sys

# ipyver only runs with ipy/clr so no point in trapping clr import as python
# run fails immediately anyway

ipyver = None #exists flag also

# This import will fail if testing in python or when runnning Sphinx
# no-Sphinx docs as clr is only in ipy/.net eviron
# See explorlib.py - on how to pass sphinx/pyhton run

import clr

# need System if "using" System for/as net type implementation
clr.AddReference("System") #no fail if .netframework 4.0+
import System

try:# if you are not embedding StdLib catch (do not need if you know)
    clr.AddReference("StdLib")
except System.IO.IOException as exc:
    print('"StdLib" not availible as AddReference') # reminds you

try:# if you are not standalone catch (do not need if you know)
    clr.AddReference("IronPython")
    import IronPython
except System.IO.IOException as exc:
    print('"IronPython" not availible as AddReference') # reminds you  
    
import json
import ipyver
import version
import time
import re
import inspect

def explore():

    print 'Loaded clr References:'        
    print(clr.References)
    print ''
    
    print 'Using ipyver to see how things are loaded:'
    print ''
    
    if ipyver:
        rss = ipyver.ReferenceStatus('json')
        rsj = rss.RefStatus()
        for k, v in rss.RefStatusIPMS().iteritems():
            print(' {}:').format(k)
            for n, a in v.iteritems():
                print('   {}:{}').format(n,a)
        print ''
        for k, v in rsj.iteritems():
            print('   {}:{}').format(k,v)
        print ''        
        rst = ipyver.ReferenceStatus('time')
        rstm = rst.RefStatus()
        for k, v in rstm.iteritems():
            print('   {}:{}').format(k,v)
        print ''
        rsr = ipyver.ReferenceStatus('re')
        rsre = rsr.RefStatus()
        for k, v in rsre.iteritems():
            print('   {}:{}').format(k,v)     
        print ''
        rstd = ipyver.ReferenceStatus('StdLib')
        rstdlib = rstd.RefStatus()
        for k, v in rstdlib.iteritems():
            print('   {}:{}').format(k,v)   
        print ''    
        rclr = ipyver.ReferenceStatus('clr')
        rclrs = rclr.RefStatus()
        for k, v in rclrs.iteritems():
            print('   {}:{}').format(k,v)   
        print ''  
    
    print 'compare to inspect.getfile'
    
    try:    
        print 'inspect ' + str(inspect.__file__)
        print 'inspect ' + str(inspect.getfile(version))
        print 'inspect ' + str(inspect.getfile(json))
    except Exception as ex:
        print(ex)    
    
    print ''
    print 'Look at globals'
    glbls = list(globals())
    for g in glbls:
        print 'g: ' + str(g)
    
if __name__ == '__main__':
    explore()