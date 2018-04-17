# -*- coding: utf-8 -*-
"""
.. created on Thu Mar 29 23:17:42 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""
LINE = 1013
clr = None #flag too
import sys
sys.path.append('../')
ipyver = None
try:
    #turn on clr also flag
    import clr #no fail if running under ipy
except Exception as exi:
    pass
if clr:# Running in ipy with clr (.net environ)
    # need System if "using" System for/as net type implementation methods
    clr.AddReference("System") #no fail if .netframework 4.0+
    import System

    try:# if you are not embedding StdLib catch (do not need if you know not needed)
        clr.AddReference("StdLib")
    except System.IO.IOException as exc:
        # reminds you to add if need or unexpected missing
        print('"StdLib" not availible as AddReference - OK if standalone')

import json
import ipyver
import version
import time
import re
import inspect

def explore(argv):
    '''
      Run explore
       
      *Use ipy.exe and this file for debugging unusual errors*
      *Need ~1500 lines to see all listed output*
      **pipe to file** ``>> output.txt`` is better
    
      params:
    
      help: [-h, -?, /?, /h, help][op] :
    
      None [opt] - look at current IronPython imports status
      output: current contents of libimports manually updated:
        - Have Passed: Have been loaded as standalone in win8.1/win7 32/64
        - Direect: via import <libname>
        - Indirect: loaded as a results of "Direct" imports
        - Imported: list of current import libs by running this module
        - NotTested: Libraries and sub-Libraries not yet tested
        - New Added: If uncommented in NotTested and recomiled, run will have output
        - list of **current** index values in NotTested list to remove on success
        - Calc'd Indirect: Passed - Direct
    
      *current contents of libimports manually updated*
      -p [opt]  - Have Passed: Have been loaded as standalone in win8.1/win7 32/64
      -d [opt]  - Direect: via import <libname>
      -i [opt]  - Indirect: loaded as a results of "Direct" imports
      -n [opt]  - NotTested: Libraries and sub-Libraries not yet tested
      -v [opt]  - run ipyver to see where assemblies and modules are sourced.
      
    '''
    args = argv[1:]
    if args:
         if '-v' in args:
            import explorver
            print 'ipyver running'
            print ''
            explorver.explore()
            return

    sysmods = set(sys.modules)

    libimport = None
    havepassed = None
    print
    try:
        import libimport
    except Exception as expt:
        print 'fail import libimport in explorlib'
        print(expt)

    try:
        sysimportmods = set(sys.modules).union(sysmods)
    except Exception as ex:
        print(ex)

    if args:
        if '-p' in args:
            print 'libimport Passed'
            print ''
            print (libimport.Passed())
            return
        if '-d' in args:
            print 'libimport Direct'
            print ''
            print (libimport.Direct())
            return
        if '-i' in args:
            print 'libimport Indirect'
            print ''
            print (libimport.Indirect())
            return
        if '-n' in args:
            print 'libimport NotTested'
            print ''
            print (libimport.NotTested())
            return

    print
    rslib = ipyver.ReferenceStatus('libimport')
    rslibs = rslib.RefStatus()
    for k, v in rslibs.iteritems():
        print('   {}:{}').format(k,v)

    print
    print 'libimport Direct'
    print ''
    print (libimport.Direct())
    print ''
    print 'libimport Indirect'
    print ''
    print (libimport.Indirect())

    havepassed = libimport.Indirect() + '\n' + libimport.Direct()
    print ''
    print 'have passed should  == Passed'
    print
    print havepassed

    print 'Look at modules after imports'
    sysimportmods = sorted(sysimportmods)
    imported = ("',\n").join(["'" + si for si in sysimportmods])
    print ''
    print 'current imported'
    print imported
    print ''
    print 'new added'
    print
    for im in imported.split('\n'):
        imr = im.replace('"','').replace(',,',',').replace("'","") \
                .replace(',','').strip()
        if not any( imr in ima for ima in libimport.Indirect().split('\n')) and \
            not any( imr in imd for imd in libimport.Direct().split('\n')):
            print im

    print
    print 'Not Tested - skipped use -n [opt]'
    print
    #print libimport.NotTested()
    if havepassed:
        hasPassed = []
        for it, noT in enumerate(libimport.NotTested().split('\n')):
            basicImport = None
            dotImport = None
            if 'from' not in noT and ' as ' not in noT:
                basicImport = \
                    noT.replace('  ',' ') \
                    .replace('import ','') \
                    .replace("'","") \
                    .replace(',','') \
                    .strip()

            if 'from' in noT and ' as ' not in noT:
                dotImport = \
                    noT.replace('  ',' ') \
                    .replace(' import ','.') \
                    .replace('from ','') \
                    .replace("'","") \
                    .replace(',','') \
                    .strip()

            if ' as ' in noT:
                basicImport = \
                    noT.split(' as ')[1].replace('  ',' ') \
                    .replace("'","") \
                    .replace(',','') \
                    .strip()

            for hp in havepassed.split('\n'):
                testimport = None
                hpr = hp.replace('"','').replace(',,',',').replace("'","") \
                        .replace(',','').strip()
                testimport = basicImport if basicImport else dotImport
                if testimport and hpr:
                    if testimport.replace("'","") == hpr:
                        hasPassed.append(('\n').join([str(it+LINE),noT.replace('"','').replace(',','')]))
        print
        print 'New Passed: Ready to clean from libimport NotTested list.'
        print 'Should be None unless you have new imports'
        print ('\n').join(hasPassed)

def getIndirect():
    '''
      Difference between hard coded maunlly updated "Passed" list and "Direct" list
      *not dynamically updated* - that is why the output is formated.
      Send output >> to file.txt copy and past into libimports then re-compile
      re-run until ok.

    '''
    import libimport
    Ind = None
    Dirct = libimport.Direct().split('\n')
    Passt = libimport.Passed().split('\n')
    Ind = list(set(Passt) - set(Dirct))
    print "Calc'd Indirect"
    print(('\n').join(sorted(Ind)))
    return Ind

if __name__ == '__main__':
    pass
#    print 'sysargv ' + str(sys.argv)
#    if any(hlp.strip() in ["-h", "-?", "/?", "/h", "help"] for hlp in sys.argv[1:]):
#        print(sys.modules['__main__'].__doc__)
#        sys.exit(0)
#
#    explore(sys.argv)
#
#    if len(sys.argv) == 1:
#        getIndirect()
#        print
#        print '* END * - Need ~1500 lines to see all above output'
