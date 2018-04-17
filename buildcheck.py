# -*- coding: utf-8 -*-
"""
.. created on Wed Feb 14 19:42:43 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""
from version import __version__
import os
import json
from build import genOutFilePath, StartBuild
from makedefault import defaultconfig, ndcDict
from partialerror import PartialErrors
from globalstate import gsBuild
import filecontrol

from buildlogs import dynfile
log = dynfile(__name__)
log.debug('\n---------------- ' + str(__name__) + \
              ' loaded ---------------')

def checkBuildConfig(usrconfig, show=False):
    '''
       Re-check to final config file

    '''
    
    userconfig = ndcDict(usrconfig)
    
    if not  all(k in userconfig.keys() for k in defaultconfig.keys()):
        log.error('\n keys {}\n\t{}' \
                  .format(str(userconfig.keys()), \
                          str(defaultconfig.keys())))
        raise KeyError('user param config key mismatched with default')
    
    if show:
        showUserConfig(userconfig)
        
    with open(userconfig['CONFIGPATH'], 'w') as jw:
        json.dump(userconfig, jw, indent=4)
    log.FILE('{}'.format(userconfig['CONFIGPATH']))

    ext = '.dll'
    if userconfig['MAKEEXE'] == True or \
        str(userconfig['MAKEEXE']).upper() == 'TRUE':
        ext = '.exe'

    outfile = genOutFilePath(userconfig['MAKEEXE'],
                             userconfig['MAINFILE'],
                             userconfig['OUTDIR'])
    
    if gsBuild.Verbose or not gsBuild.INFO:
        log.info('\nOK - Reading Configuration file:\n {}' \
                 .format(userconfig['CONFIGPATH']))
        log.info('\nOK - Building file {}\nOK - output typ :  {}\n ' \
                 .format(outfile, ext[1:].upper()))

    reqlst = None

    if 'Tests' in os.getcwd():
        log.warn('\n Tests in cwd {}'.format(os.getcwd()))
        reqlst = filecontrol.checkRequired('../unittest.txt')
    reqlst = filecontrol.checkRequired('requirements.txt')

    if PartialErrors:
        log.info('\nERR - Partial Error - check output for partial errors')

    elif not reqlst:
        if gsBuild.Verbose or not gsBuild.INFO:
            log.info('\nOK - requirements found:\n')

    elif reqlst:
        log.warn(('\nSome How Fail - requirements NOT found:\n' + \
                  '    *missing {}\n'*len(reqlst)).format(*reqlst))
    if 'Tests' not in os.getcwd():
        StartBuild(userconfig['CONFIGPATH'])
    return True

def showUserConfig(configuration):
    '''
	    Output the configuration file

	 '''
    if gsBuild.Verbose:
        log.info('\nBuild config:\n  {}' \
                 .format(json.dumps(configuration, indent=4)))

if __name__ == '__main__':
    pass
