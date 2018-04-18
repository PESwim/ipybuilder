# -*- coding: utf-8 -*-
"""
.. created on Sat Mar 17 20:35:40 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""
from version import __version__
import os
from os import path as op
from os.path import exists as opex
from os.path import join as opj
from os.path import normpath as opn
from os.path import dirname as opd
from os.path import abspath as opab
from globalstate import gsBuild

if __name__ != '__main__':

    from partialerror import FatalError, partialError
    from makedefault import DefaultReqList
    from buildlogs import dynfile
    log = dynfile(__name__)
    log.debug('\n---------------- ' + str(__name__) + \
                  ' loaded ---------------')

gsBuild.REQUIRED = []
gsBuild.HAVELIB = False
gsBuild.HAVELIBDLL = False
gsBuild.requiredPath = 'requirements.txt'
gsBuild.IRONPYTHON = 'License.StdLib.txt'

def FindIronPython():
    '''
      Walk directories to find IronPython Install

      :return: IronPython install path [str] - or - if not main sets gsBuild.IPATH

      :raise: NotImplementedError

    '''

    SEARCHUSER = opn(os.path.expanduser('~'))

    SEARCHCWD = opd(os.getcwd())
    if 'Tests' in os.getcwd():
        SEARCHCWD = opd(SEARCHCWD)
    SEARCHMODSRC = opn(opd(opd(os.__file__)))
    SEARCHROOT = os.path.splitdrive(SEARCHCWD)[0]

    searchList = [SEARCHCWD, SEARCHUSER, SEARCHMODSRC, SEARCHROOT]

    for direct in searchList:
            for root, dirs, files in os.walk(direct, topdown=False):
                for name in files:
                        if gsBuild.IRONPYTHON in name:
                            with open(opn(opab(opj(os.getcwd(), 
                                                   'defaults\\ipath.txt'))),
                                                   'w') as tw:
                                tw.write(opd(opn(opj(root, name))))
                                
                            return opd(opn(opj(root, name)))
                        
    if __name__ == '__main__':
        raise NotImplementedError('Failed to Find/*Access' + \
                     ' loadable IronPython Distribution')

    log.warn(('\nFailed to find loadable IronPython Distribution:\n Used "{}"' + \
              ' name to search for directory.\n\n' +
              '   Searched ordered from base:\n {}\n {}\n {}\n {}\n') \
            .format(gsBuild.IRONPYTHON, *searchList))

    log.info('\nCheck Access and/or install IronPython to loadable path.')

    raise FatalError('NotImplementedError', 'Failed to Find/*Access' + \
                     ' loadable IronPython Distribution')

def checkRequiredIP():
    if gsBuild.IPATH:
        return
    
    gsBuild.HAVELIB
    gsBuild.HAVELIBDLL
    ironPythonPath = FindIronPython()

    if opex(ironPythonPath):
        gsBuild.IPATH = ironPythonPath

    userReqBaseLst = os.listdir(ironPythonPath)
    userReqLst = [opn(opj(ironPythonPath, urf)) for urf in  os.listdir(ironPythonPath)]

    if opex(opj(ironPythonPath, 'Lib')):
        log.FILE('Exists: {}'.format(opj(ironPythonPath, 'Lib')))
        gsBuild.HAVELIB = True

    # TODO check for downloaded StdLib
    if op.isfile(opn(opj(ironPythonPath, 'StdLib.dll'))):
        gsBuild.HAVELIBDLL = True

    if not all(rf in userReqBaseLst for rf in DefaultReqList):
        try:
            raise NotImplementedError
        except NotImplementedError as ex:
            msg = 'Failed to find all required IronPython Distribution files'
            partialError(ex, msg)

    log.FILE('\n Exists required path {}'.format(opj(os.getcwd(), gsBuild.requiredPath)))
    WD = os.getcwd()
    if 'Tests' in WD:
        WD = opd(WD)
    with open(opj(os.getcwd(), gsBuild.requiredPath), 'w') as tw:
         for f in userReqLst:
             relp = opn(op.relpath(f))
             # skip dirs

             if op.isfile(relp):
                 tw.write(opn(os.path.relpath(f)) + '\n')
    log.FILE('Exists {}'.format(gsBuild.requiredPath))

    return

if __name__ == '__main__':
    
    gsBuild.IRONPYTHON = 'License.StdLib.txt'
    print('IronPyhton found by looking for: "{}"\nInstalled in:\n\t{}' \
           .format(gsBuild.IRONPYTHON, FindIronPython()))
