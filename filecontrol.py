# -*- coding: utf-8 -*-
"""
.. Created on Sat Mar 03 13:53:34 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.
   
   *logging file queries*
   
"""
from version import __version__
import sys
import os
import re
import time

from partialerror import partialError
from makeload import getTrueFilePath

from buildlogs import dynfile
log = dynfile(__name__)
log.debug('\n---------------- ' + str(__name__) + \
              ' loaded ---------------')

LOOKBACKSEC = 120

def checkRequired(path):
    '''
       Read file list of required files and check they
       if exist or partial error.

       :param:
           - path [str] - of file to read list
           - tag= [opt][str] - writelog tag for filtering

       :return: list of files **not** found - should be empty [list]

       :raise: partialError - sink errors for stdout in PartialErrors [list]

    '''
    tag = 'Exists'
    reqpath = getTrueFilePath(path)
    amsg = 'need {} file'.format(reqpath)
    assert os.path.isfile(reqpath), amsg

    with open(reqpath, 'r') as txtr:
        reqfiles = txtr.readlines()
        log.FILE('{} {}'.format(tag, path))

    reqfs = list(reqfiles)
    for f in reqfiles:

        try:
            fp = getTrueFilePath(f.strip())
            log.FILE('{} {}'.format(tag, fp))
            reqfs.remove(f)
        except IOError as ex:
            log.debug('raise partial')
            partialError(ex, ex.message)
            continue

    return reqfs

def delTestFileWrites(dellst):
    '''
       Handle test file cleanup delete created files

       :param: dellst [list] - list log files filtered for deletion

       :return: True [bool] - if all dellst files deleted

    '''

    haveDeleted = []
    for f in dellst:
        if os.path.isfile(f):
            os.remove(f)
            haveDeleted.append(f)
            log.FILE('\n Deleted: {}'.format(f))

    return haveDeleted

def getFilesDeleted(loglst):
    '''
       Handle deletion of test generated files that have been
       parsed and filtered in logfile list.

       :param: loglst [list] - list log files during lookback

       :return: [list] - existing files

    '''
    bldfileDeleted = []
    for fl in loglst:
        if 'Deleted' in fl and '____' not in fl:
            bldfileDeleted.append(fl)

    return bldfileDeleted

def getFilesExist(loglst):
    '''
       Handle parsed and filtered logfile list

       :param: loglst [list] - list log files during lookback

       :return: [list] - existing files

    '''

    bldfileConfirmed = []
    for fl in loglst:
        if 'Exists' in fl and '____' not in fl:
            bldfileConfirmed.append(fl.strip())

    return bldfileConfirmed

def CompareFilesConfirmedToRequired(confirmlst, reqlst):
    '''
       Handle parsed and filtered logfile list

       :param:
           - confirmlst [list] - log files confirmed during lookback
			  - reqlst [list] - log files that should be in confirmed list

	   :return: [list] - non-conformed files - should return []

    '''
    cflst = list(reqlst)
    for cl in (confirmlst):
        if cl in reqlst:
            cflst.remove(cl)
    return cflst

def getFilesWritten(loglst):
    '''
       Handle parsed and filtered logfile list

       :param: loglst [list] - list log files during lookback

       :return: [list] - written files

    '''
    fileWrites = []
    for fl in loglst:
        if fl.strip() and 'Exists' not in fl and \
        'Confirmed' not in fl and '____' not in fl:
            fileWrites.append(fl.strip())

    if fileWrites:
        return fileWrites

    return None

def getFilesConfirmed(loglst):
    '''
       Handle parsed and filtered logfile list

       :param: loglst [list] - list log files during lookback

       :return: [list] - existing files

    '''
    fileConfirmed = []
    for fl in loglst:
        if 'Confirmed' in fl and '____' not in fl:
            fileConfirmed.append(fl.strip())

    if fileConfirmed:
        return fileConfirmed
    return None
def delBuildFileWrites(dellst):
    '''
       Handle build file cleanup delete created files

       :param: dellst [list] - list log files filter for deletion

       :return: status True [bool] - if all dellst files deleted

    '''
    for f in dellst:
        if os.path.isfile(f):
            sys.path.remove(f)
    return True
def setLogLookBackTimeSec(lookback=120):
    '''
       Set log output look-back time (sec)

       :param: sec [int]

    '''
    global LOOKBACKSEC
    LOOKBACKSEC = lookback
    log.info('\n set lookback: {} sec'.format(LOOKBACKSEC))
    return None

def getLogLookBackTimeSec():
    '''
       Get log output look-back time (sec)

       :return: sec [int]

    '''
    global LOOKBACKSEC
    return LOOKBACKSEC

def checkLogTimeSec(strline, lookBackSec, tag):

    regxlt = re.compile('([0-9/]+?)\s([0-9:]+[0-9])')

    strlogtime = regxlt.findall(strline.strip())
    lng = None
    if strlogtime:
        lng = strlogtime[0][0]

    tstrp = None
    if lng and len(lng) == 8:
        tstrp = time.strptime(lng + ' ' + strlogtime[0][1], '%x %X')
        curDay = '_' + time.strftime('%x', time.localtime())

    if tstrp and curDay in strline.strip() and \
        time.mktime(tstrp) > lookBackSec and tag in strline.strip():
        return True

    return False

def getWriteLog(tag=''):
    '''
       Find writelog lines matching timestamps between
       lookbacktime (default 120 sec back) and current local time

       logpath: cwd\\UserDefaulted\\filewrite.log - no limit storage

       :param: tag= [str] - filter by tag

       :return: writelog data [list]

    '''

    global LOOKBACKSEC
    writelogs = []
    WD = os.getcwd()
    logpath = os.path.join(WD, 'UserDefaulted\\filewrite_default.log')
    # ref methods
    #    curDateTime = time.strftime('%x %X',time.localtime())
    #    import datetime as dt
    #    lookBackTime = dt.datetime.fromtimestamp(lookBackSec).strftime('%X')
    #    tstrp = time.strptime(time.strftime('%x %X',time.localtime()),'%x %X')
    #    logTimeSec = time.mktime(tstrp)

    lookBackSec = time.time()-LOOKBACKSEC
    f_start = False
    with open(logpath, 'r') as lr:
        logfile = lr.readlines()

    for ln in logfile:
        if not f_start and checkLogTimeSec(ln, lookBackSec, tag):
            f_start = True

        if f_start and '*-' in ln and  '*Missing' not in ln:
            writelogs.append(ln.replace('*-', '').replace('-*', ''))

    return list(set(writelogs))

if __name__ == '__main__':
    pass
