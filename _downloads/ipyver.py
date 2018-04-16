# -*- coding: utf-8 -*-
"""
.. created on Fri Mar 16 11:23:30 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""
import os
import sys
clr = None
from version import __version__
try:
    import clr
    clr.AddReference("System")
    import System
    from System import AppDomain
    from System.Reflection import Assembly
except Exception as exi:
    pass

if not clr:
    print 'Must run under ipy/clr'    

class ReferenceStatus(object):
    '''
      Check clr Reference Status - ipy **Only**

      :use:refStat = ReferenceStatus().RefStatus()

      :param: reference name  [opt] [str] - check against loaded

      class and instance method returns:
        - cls.RefStatus() if pararm: reference name
        - cls.RefStatusIPMS() for any instance
      
      :return: status [dict] - None on fail/err
          keys: 'sys' - System and 'ipy' IronPython
            or no key for reference name return:
          subkeys:
            'ver' [str]
            'isLocal' [bool]
            'isloaded' [bool]
            'path' [str]
            'name' [str]

             

      Example:
    
      .. code-block::  python
    
        try:
            import inspect
        except ImportError as ex:
            pass

        rsp = ReferenceStatus('inspect').RefStatus()
        for k, v in rsp.iteritems():
            print('inspect {}:{}'.format(k,v))

        or 
        
        rsp = ReferenceStatus().RefStatusIPMS()
        for k, v in rsp.iteritems():
            print('IPMS {}:{}'.format(k,v))

    '''
    _ipms = {'sys': {'name'    :'System',
                     'ver'     :None,
                     'isLocal' :None,
                     'isloaded':False,
                     'path'    :None},
             'ipy': {'name'    :'IronPython',
                     'ver'     :None,
                     'isLocal' :None,
                     'isloaded':False,
                     'path'    :None}
            }

    _aref = {'name'    :None,
             'ver'     :None,
             'isLocal' :None,
             'isloaded':False,
             'path'    :None
            }
    _stdAss = ['mscorlib', 'System',
               'Microsoft', 'IronPython',
               'ipy'
              ]

    found = None

    def __init__(self, ref=None):
        
        if not clr:
            return
        self.ref = ref
        self.assemblies = AppDomain.CurrentDomain.GetAssemblies()
        self.appName = AppDomain.CurrentDomain.FriendlyName
        self._getAssemblyInfo()
        self.found = False

    def RefStatus(self):
        if self.ref:
            return(self._aref)
        return None

    def RefStatusIPMS(self):
        return(self._ipms)

    def _getModules(self):
#        print 'RUNNING GETMODS'
        if self.ref and any(self.ref in sm for sm in sys.modules):
            fnp = None

            try:
                fnp = sys.modules[self.ref].__file__
            except AttributeError:
                fnp = 'Internal'
                if any(self.ref in bltn for bltn in sys.builtin_module_names):
                    fnp = 'Built-In-Module'
#            print 'FNP ' + str(fnp) 
            if fnp:
                self._aref['isloaded'] = True

            if self.ref in fnp and ':' in fnp:
                self._aref['isLocal'] = False

            if ('Int' in fnp or 'Built-In' in fnp or self.ref in fnp) and ':' not in fnp:
                self._aref['isLocal'] = True
            
            self._aref['path'] = fnp

            if 'Built' in fnp:
                return True

            ver = None
            version = None
            version = [v for v in dir(sys.modules[self.ref]) \
                       if 'ver' in v.lower()]

            if version:
                ver = getattr(sys.modules[self.ref], version[0])
            else:
                try:
                    ver = sys.modules[self.ref].__version__
                except AttributeError as ex:
                    try:
                        ver = sys.modules[self.ref].version
                    except AttributeError as exc:
                            pass
            self._aref['ver'] = ver
            return True
        return False

    def _getAssemblyInfo(self):
        
        if not self.assemblies and not self.ref:
            return
        for ass in self.assemblies:
            realass = clr.Convert(ass, Assembly)
            realassCode = None
            realassLoc = None
            realassVer = None
            realassName = None
            #print realass.GetName().ToString()
            try:
                realassVer = realass.GetName().Version.ToString()
            except (System.NotSupportedException, System.MissingMemberException):
                pass
            try:
                realassCode = realass.CodeBase
            except (System.NotSupportedException, System.MissingMemberException):
                pass
            try:
                realassLoc = realass.Location
            except (System.NotSupportedException, System.MissingMemberException):
                pass

            if realass:
                if realass.GetName() and 'System' in realass.GetName().Name and \
                    '.' not in realass.GetName().Name:
    
                    self._ipms['sys']['isloaded'] = True
                    if realassVer:
                        self._ipms['sys']['ver'] = realassVer
                        
                    if realassCode:
                        if 'GAC' in realassCode:
                            self._ipms['sys']['isLocal'] = False
                        elif self.appName.strip() in realassCode:
                                self._ipms['sys']['isLocal'] = True
    
                        self._ipms['sys']['path'] = realassCode
    
                    if not realassCode and realassLoc == '':
                        self._ipms['sys']['isLocal'] = True
    
                if 'IronPython' in realass.GetName().Name and \
                    '.' not in realass.GetName().Name:
                    self._ipms['ipy']['isloaded'] = True
                    if realassVer:
                        self._ipms['ipy']['ver'] = realassVer
    
                    if realassCode:
                        if 'GAC' in realassCode:
                            self._ipms['ipy']['isLocal'] = False
    
                        elif self.appName.strip() in realassCode:
                            self._ipms['ipy']['isLocal'] = True
    
                        self._ipms['ipy']['path'] = realassCode
    
                    if not realassCode and realassLoc == '':
                         self._ipms['ipy']['isLocal'] = True
            
           
            sep = ','
            assert len(sep) == 1, 'bad sep format'
            
            if self.ref:
                if all(std not in realass.GetName().Name \
                       for std in self._stdAss):

                    self._aref['name'] = self.ref

                    #reset to make sure it matches with name found in realass
                    realassVer = None
                    realassCode = None
                    realassLoc = None
                    realassName = None
                   
                    try:
                        realassName = realass.GetName().Name
                    except Exception as ex:
                        pass
          
            if self.ref and realassName and self.ref in realassName:
                try:
                    realassVer = realass.GetName().Version.ToString()
                except Exception as exa:
                    pass
                try:
                    realassCode = realass.CodeBase
                except Exception as exb:
                    pass
                try:
                    realassLoc = realass.Location
                except Exception as exc:
                    pass

                if realassVer:
                    self.found = True
                    self._aref['isloaded'] = True
                    self._aref['ver'] = realassVer
  
                if realassCode:
                    self._aref['path'] = realassCode
                    
                    if 'GAC' in realassCode:
                        self._aref['isLocal'] = False

                    elif self.ref in realassCode:
                        self._aref['isLocal'] = False
                        
                    if self.ref in realassCode and ':' not in realassCode:
                        self._aref['isLocal'] = True
    
                elif not realassCode:
                    if realassLoc == '':
                        self._aref['isLocal'] = True
                        
            elif self.ref and sys and not self.found or \
                (self.ref and not 'StdLib' in self.ref and \
                 realassVer == "0.0.0.0"):
                self.found = self._getModules()
                
            if self.ref and not self.found and 'StdLib' not in self.ref:
                self._aref = {self.ref:'Not Found'}
        
        if self.ref and sys and not self.found and not 'StdLib' in self.ref:
            self.found = self._getModules()

if __name__ == '__main__':
    pass
