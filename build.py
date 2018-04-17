# -*- coding: utf-8 -*-
"""
.. created on Wed Feb 14 19:50:03 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""
from version import __version__
import os
import json
import buildmake

from buildlogs import dynfile
log = dynfile(__name__)
log.debug('\n---------------- ' + str(__name__) + \
              ' loaded --------------------')

def StartBuild(configPath):
    '''
	    Intermediate helper to set-up makeBuild and run
	   
    '''

    buildconfig = None
    with open(configPath, 'r') as jbcr:
        buildconfig = json.load(jbcr)
    log.FILE('Confirmed: {}'.format(configPath))

    buildmake.makeBuild(buildconfig)

    return True

def genOutFilePath(makeexe, main, odir):

    ext = '.exe'
    if not makeexe:
        ext = '.dll'

    return os.path.join(odir, main.split('.')[0] + ext)

if __name__ == '__main__':
    pass
