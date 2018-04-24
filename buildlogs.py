# -*- coding: utf-8 -*-
"""
.. created: on Sat Feb 17 19:43:20 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

  *logging with termialC stream subclass*

"""
from version import __version__
import sys
import os
import logging
import time
from terminalcolorlog import terminalC
from globalstate import gsBuild

#  *** check log level before finish ***
# ------------  stdout formats -----------------------------
FORMTSTR = "[%(levelname)-5.5s] [%(asctime)s]" + \
           "[%(funcName)s]:ln:[%(lineno)d] %(message)s"

FORMTINFO = "%(message)s"
FORMTDATE = "%Y-%m-%d %H:%M:%S"
#------------- file write log and format ---------------------
if not os.path.isdir(os.path.join(os.getcwd(), 'UserDefaulted')):
    os.mkdir(os.path.join(os.getcwd(), 'UserDefaulted'))

LOGFILE = os.path.join(os.getcwd(), 'UserDefaulted', 'filewrite_default.log')
FORMTFILE = "[%(asctime)s] %(module)s - file write:\n  *- %(message)s -*\n"

#need global single instance log
log = None
HILO_DEBUG = (40, 0)
HILO_INFO = (40, 20)
FILELVL = 45

class func(object):
    ''' 
       *"logging"* way to filter by each FILE record at lvl 45.
       Also use custom level to only send level 45 to filelog
       if log.critical = 50 then log console goes to File.
    
    '''

    def __init__(self, hi, lo):
        self.hi = hi
        self.lo = lo
        super(func, self).__init__()

    def filter(self, rec):
        return True if rec.levelno <= self.hi and \
            rec.levelno >= self.lo else False

# dynamic file handler
def dynfile(name, pathfilelog=None):
    ''' split log files and log console by lvl and filter'''

    fpath = pathfilelog
    if not fpath:
        fpath = os.path.join(os.getcwd(), LOGFILE) # or 'testlog.log'
    logging.addLevelName(FILELVL, "FILE")

    def logfile(self, message, *args, **kws):
        if self.isEnabledFor(FILELVL):
            self._log(FILELVL, message, args, **kws)

    logging.Logger.FILE = logfile
    logging.FILE = FILELVL

    # take out existing handlers or duplicate entries
    loghands = list(logging.getLogger('').handlers)
    for hndl in loghands:
        logging.getLogger('').removeHandler(hndl)
        hndl.close()

    ufileFormatter = logging.Formatter(FORMTFILE)
    ufileFormatter.datefmt = FORMTDATE
    ufileHandler = logging.FileHandler(fpath)
    ufileHandler.setFormatter(ufileFormatter)
    ufileHandler.setLevel(logging.FILE)
    logging.getLogger('').addHandler(ufileHandler)

    if gsBuild.INFO:
        infoFormatter = logging.Formatter(FORMTINFO)
        infoFormatter.datefmt = FORMTDATE
        iHandler = terminalC()#logging.StreamHandler(stream=sys.stdout)
        iHandler.setFormatter(infoFormatter)
        iHandler.setLevel(logging.INFO)
        cifunc = func(*HILO_INFO)
        iHandler.addFilter(cifunc)
        logging.getLogger('').addHandler(iHandler)

    else:
        debugFormatter = logging.Formatter(FORMTSTR)
        debugFormatter.datefmt = FORMTDATE
        #logging.StreamHandler(stream=sys.stdout)
        dHandler = terminalC(sys.stdout)
        dHandler.setFormatter(debugFormatter)
        dHandler.setLevel(logging.DEBUG)
        cdfunc = func(*HILO_DEBUG)
        dHandler.addFilter(cdfunc)
        logging.getLogger('').addHandler(dHandler)

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    if gsBuild.INFO:
        log.setLevel(logging.INFO)

    if name == '__main__' and len(log.handlers) == 0:
        log.FILE('______________' + \
                 str(time.strftime('%x %X', time.localtime())) + \
                       '____________')

    elif name == '__main__':

        log.debug('\n---------------- ' + str(__name__) + \
              ' loaded ----------------')

        log.info(('\n---------------- logging FILE level {} '+ \
              '-----------').format(logging.FILE))

    return log
if __name__ == '__main__':
    pass
