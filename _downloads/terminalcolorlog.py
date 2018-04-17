# -*- coding: utf-8 -*-
"""
.. created on Wed Feb 21 23:44:33 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""
from version import __version__
import sys
import logging

class terminalC(logging.StreamHandler):
    ''' Sheds light on a dark subject.
    
        Uses wincon and winbase constants and handles
        or ANSI codes for platform specific awesomeness
        in concert with with logging.
        
        *Sad note: that if you run* **bash** *in windows you 
        must manually tweak the "code" for bash. 
        No-way to know what tty your running*
        
        *Glad note: it works in bash mingw win 64*
        
        .. code-block:: python
           :lineno-start: 87
           :emphasize-lines: 3
           
           def assignColor(self):
               if 'win' in sys.platform:
                   self.setColor = self.emitWin
               else:
                   self.setColor = self.emitAnsi
				   
	   :TODO: add cmd on-the-fly switch to instantiated class
	   between bash and windows

    '''
    
    _winc = {
            'FGRND_BLUE'      : 0x0001,
            'FGRND_GREEN'     : 0x0002,
            'FGRND_RED'       : 0x0004,
            'FGRND_WHITE'     : 0x0001 | 0x0002 | 0x0004,
            'FGRND_BLACK'     : 0x0000,
            'FGRND_CYAN'      : 0x0003,
            'FGRND_MAGENTA'   : 0x0005,
            'FGRND_YELLOW'    : 0x0006,
            'FGRND_GREY'      : 0x0007,
            'FGRND_BOLD'      : 0x0008,
            'BGRND_BLACK'     : 0x0000,
            'BGRND_BLUE'      : 0x0010,
            'BGRND_GREEN'     : 0x0020,
            'BGRND_CYAN'      : 0x0030,
            'BGRND_RED'       : 0x0040,
            'BGRND_MAGENTA'   : 0x0050,
            'BGRND_YELLOW'    : 0x0060,
            'BGRND_GREY'      : 0x0070,
            'BGRND_BOLD'      : 0x0080
            }
    _winh = {
            'INPUT_HNDL'      : -0xA,
            'OUTPUT_HNDL'     : -0xB,
            'ERROR_HNDL'      : -0xC
             }
    _ansi = {
            '50' :'\x1b[0;31m', # red
            '40' :'\x1b[1;31m', # red hi
            '30' :'\x1b[1;33m', # yellow
            '20' :'\x1b[1;32m', # green 
            '10' :'\x1b[0;0m',  # white
            'STD':'\x1b[0m'   # normal
            }
    _ln = None
    
    def __init__(self,stream=sys.stdout):
        import ctypes
        super(terminalC,self).__init__(stream)
        self.setColor = None
        self.ctypes = ctypes
        self.lvlno = None
        self.msg = None
        self.cls = terminalC
        self.usrout = stream
        self.emits = self.emit
        if self.usrout == sys.stdout or self.usroout == sys.stderr:
            self.outhndl = self.ctypes.windll.kernel32 \
                           .GetStdHandle(self.winh('OUTPUT_HNDL'))
            self.assignColor()
            self.emit = self.setColor
        assert self.emits != self.emit
        
    def assignColor(self):
        if 'win' in sys.platform:#if compiling in bash will set to Ansi
            self.setColor = self.emitWin#self.emitAnsi#
        else:
            self.setColor = self.emitWin#self.emitAnsi
    
    def winc(self, key):
        return(self._winc[key])

    def winh(self, key):
        return(self._winh[key])
    
    def cLWin(self,lvlno):
        if lvlno >= 50:
            return  self._winc['FGRND_RED'] | self._winc['FGRND_BOLD']
        elif lvlno >= 40:
            return self._winc['FGRND_RED'] | self._winc['FGRND_BOLD']
        elif lvlno >= 30:
            return self._winc['FGRND_YELLOW'] | self._winc['FGRND_BOLD']
        elif lvlno >= 20:
            return self._winc['FGRND_GREEN'] | self._winc['FGRND_BOLD']
        elif lvlno >= 10:
            return self._winc['FGRND_MAGENTA']
        else:
            return self._winc['FGRND_WHITE']
    
    def cLAnsi(self,lvlno):
        if lvlno >= 50:
            return self._ansi['50'] #| self._winc['FGRND_BOLD']
        elif lvlno >= 40:
            return self._ansi['40']
        elif lvlno >= 30:
            return self._ansi['30']
        elif lvlno >= 20:
            return self._ansi['20']
        elif lvlno >= 10:
            return self._ansi['10']
        else:
            return self._ansi['STD']
        
    def emitWin(self, rec):
        self.lvlno = rec.levelno
        winclr = self.cLWin(rec.levelno)
        winstd = self.cLWin(0)
        self.ctypes.windll.kernel32.SetConsoleTextAttribute(self.outhndl, winclr)
        self.emits(rec)
        self.ctypes.windll.kernel32.SetConsoleTextAttribute(self.outhndl, winstd)

    def emitAnsi(self, rec):
        self.lvlno = rec.levelno
        self.msg = rec.msg
        ansimsg = self.cLAnsi(rec.levelno) + self.msg + self.cLAnsi(0)
        rec.msg = ansimsg
        self.emits(rec)
    
if __name__ == '__main__':
    pass
