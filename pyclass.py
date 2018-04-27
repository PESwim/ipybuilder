# -*- coding: utf-8 -*-
"""
.. created on Thu May 10 00:50:55 2018
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

class hndlFileStreams():
    _handles = []
    _closes = []
    _fdic = {}
    _closed = []

    def __init__(self):
        pass
    
    def fdic(self, key=None, skey=None, val=None):
        if key and skey and val:
            if key in self._fdic.keys():
                if skey in self._fdic[key].keys():
                    self._fdic[key][skey] = val
                else:
                    self._fdic[key].update({skey:val})    
            else:
                self._fdic.update({key:{skey:val}})    
        elif key == skey == val == None:
            return self._fdic
    
    @property
    def handles(self):
        return self._handles
    
    @handles.setter
    def handles(self,val):
        assert isinstance(val, list), 'need list for handle [name, path, strm.handle]'
        self._handles.append(val)

    @property
    def closed(self):
        return self._closed

    def closes(self, val):
        assert isinstance(val, list), 'need list for handle [name, strm.handle]'
        haveHndl = False
        haveName = False
        if not len(val) > 0:
            print 'Execution or syntax error: nothing to close'
        elif val and len(val) >= 2:
            haveHndl = val[1]
            haveName = val[0]
        if haveHndl:
            for i, hndl in enumerate(self.handles):
                if hndl[-1] == haveHndl:
                    self._closed.append(self.handles[i])
                    del self.handles[i]
                    haveName = None
        if haveName:
            for j, name in enumerate(self.handles):
                name = name.replace('Dll.','').replace('IPDll.','')
                hname = haveName.replace('Dll.','').replace('IPDll.','')
                if name == hname:
                    self._closed.append(self.handles[i])
                    del self.handles[i]

    def hndlReport(self, typ='handles'):
        rptTyp = 'Open'
        rpt = ''
        obj = None
        if typ == 'handles':
            obj = self.handles
        elif not typ or typ == 'closed' and self._closed:
            obj = self._closed
            rptTyp = 'Closed'

        rpt = ('\nHandles Report - ' + '{}:\n {:_<20}{:_^30}{:_>10}\n') \
              .format(rptTyp, 'Name', 'Path', 'Hndl') 
        if obj:
            for vals in obj:
                rpt = rpt + '\n'
                if vals:
                    rpt = rpt + ' {:<20}'.format(str(vals[0])) 
                if vals and len(vals) >= 2 and vals[1]:
                    rpt = rpt + ' {:<30}'.format(str(vals[1]))     
                if vals and len(vals) == 3 and vals[2]:
                    if isinstance(vals[2], System.IntPtr):
                        vals[2] = int(vals[2])
                        rpt = rpt + '{:>10}'.format(str(vals[2]))
        else:
            rpt = rpt + ' {:<20}{:<30}{:>10}'.format('null', 'null', 'null')
        return rpt