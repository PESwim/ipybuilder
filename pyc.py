# -*- coding: utf-8 -*-
#####################################################################################
#
#  Copyright (c) Microsoft Corporation. All rights reserved.
#
# This source code is subject to terms and conditions of the Apache License, Version 2.0. A
# copy of the license can be found in the License.html file at the root of this distribution. If
# you cannot locate the  Apache License, Version 2.0, please send an email to
# ironpy@microsoft.com. By using this source code in any fashion, you are agreeing to be bound
# by the terms of the Apache License, Version 2.0.
#
# Copyright 2018 - Howard Dunn - PE LLC. Apache 2.0 v.2 licensed. Modified/derivative work from original.
#
#
# Modification not endorsed by Microsoft Corp. or Secret Labs AB
#
# You must not remove this notice, or any other, from this software.
#
#####################################################################################

"""
    pyc: The Command-Line Python Compiler
    \
       
    Usage: ipy.exe pyc.py [options] file [file ...]
    \
  
    ::
        
     Options:
      /out:output_file                          Output file name (default is main_file.<extenstion>)
      /target:dll                               Compile only into dll.  Default
      /target:exe                               Generate console executable stub for startup in addition to dll.
      /target:winexe           TODO             Generate windows executable stub for startup in addition to dll.
      @<file>                  NOT TESTED       Specifies a response file to be parsed for input files and command line options (one per line)
      /file_version:<version>  NOT IMPLEMENTED  Set the file/assembly version
      /? /h                                     This message
      -v - in ipybuild args                     Verbose output

    ::
        
      EXE/WinEXE specific options:
        /main:main_file.py                        Main file of the project (module to be executed first)
        /platform:x86                             Compile for x86 only
        /platform:x64                             Compile for x64 only
        /embed                                    Embeds the generated DLL as a resource into the executable which is loaded at runtime
        /libembed                                 Embeds the StdLib DLL as a resource into the executable which is loaded at runtime
        /mta                                      Set MTAThreadAttribute on Main instead of STAThreadAttribute, only valid for /target:winexe
        /file_info_product:<name>                 Set product name in executable meta information
        /file_info_product_version:<version>      Set product version in executable meta information
        /file_info_company:<name>                 Set company name in executable meta information
        /file_info_copyright:<info>               Set copyright information in executable meta information
        /file_info_trademark:<info>               Set trademark information in executable meta information
    
    ::
      
      Example:
        ipy.exe pyc.py /main:Program.py mian.py /target:exe

"""
from version import __version__
clr = None
import sys
import pyclass
from pyclass import hndlFileStreams
import time
try:
    import clr
    clr.AddReference("IronPython")
    clr.AddReference("IronPython.Modules")
    clr.AddReference("System")
    from System.Collections.Generic import List
    import IronPython.Hosting as Hosting
    from IronPython.Runtime.Operations import PythonOps
    import System
    from System import IO
    from System import Version
    from System.Reflection import Emit, Assembly
    from System.Reflection.Emit import OpCodes, AssemblyBuilderAccess
    from System.Reflection import (AssemblyName, TypeAttributes,
                                   MethodAttributes, ResourceAttributes,
                                   CallingConventions)

except Exception as exi:
    print('Import Error in pyc: one possible cause - no clr\n\t' + str(exi))

internalDlls = ['Dll.IronPython', 'Dll.IronPython.Modules',
                'Dll.IronPython.Wpf', 'Dll.IronPython.SQLite', 'Dll.StdLib',
                'Dll.Microsoft.Scripting', 'Dll.Microsoft.Dynamic'
                ]

class PythonDynamic(object):
    '''
      PythonDynamic class - runs detailed check and reource loading
      specifically implemented to run ipybuilder.exe - Stanalone IronPython compiler.

      Use the ipybuilder.exe or ipybuild.py [-v] arg to get full output

      5/26/2018 Copyright 2018 - hdunn. Apache 2.0 licensed.

      Modified Code from original pyc.py

    '''
     # 5/26/2018 Copyright 2018 - hdunn. Apache 2.0 licensed.
     #----- Modified Code  -------

    #ReqDlls
    _ReqCoreAndDllNamesAndSrcPathAndType = None
    #loadedDlls
    _LoadedCoreAndDllNames = None
    #NotLoadedDlls
    _NotLoadedCoreAndDllNames = None
    #DllsNotAvail
    _ReqDllCoreNotAvialible = None
    #ResAvail
    _ResourceCoreAvailibleAndSrcPathAndType = None
    #ResNotAvail
    _ResourceCoreNotAvilible = None
    #ReqRes
    _ResourceReqCoreAndSrcPathAndType = None
    #LoadedRes
    _LoadedResourceCore = None
    #NonLoadedRes
    _NotLoadedResourceCore = None

    def __init__(self, config, assName, intDlls):

        self.config = config
        self.ab = None
        self.mb = None
        self.tb = None
        self.Name = assName
        self.AssemblyName = assName
        self.verbose = config.verbose
        self.intDlls = list(intDlls)
        self.dllNames = None
        self.embedDict = None
        self.MemDlls = None
        self.MemBytes = None
        self.MemStrm = None
        self.MemIdxToClose = []
        self.MemRes = None
        self.TmpDir  = None
        self.TmpDirInfo = None
        #initialize -w/ wo/ StdLib
        if not self.config.libembed:
                self.intDlls.remove('Dll.StdLib')
        self.ReqDlls(dllList=self.intDlls)#internalDlls
        self.initialize()

    def initialize(self):
        self.createTmpDirectory()
        self.ab = PythonOps.DefineDynamicAssembly(self.Name, AssemblyBuilderAccess.RunAndSave)
        self.ab.DefineVersionInfoResource(self.config.file_info_product,
                                     self.config.file_info_product_version,
                                     self.config.file_info_company,
                                     self.config.file_info_copyright,
                                     self.config.file_info_trademark)

        self.mb = self.ab.DefineDynamicModule(self.config.output, self.Name.Name + ".exe")
        self.tb = self.mb.DefineType("PythonMain", TypeAttributes.Public)
        self.setReqRes()
        self.setNotLoadedRes()
        self.mapResAvail()
        self.setResNotAvail()
        self._NotLoadedCoreAndDllNames = self._NotLoadedResourceCore

        return

    def setReqRes(self):
        
        ReqDllDic = self.ReqDlls()
        for k in ReqDllDic.keys():
            self.ReqRes(resName=ReqDllDic[k]['DLL'])

    def setNotLoadedRes(self):

        NotResDic = self.ReqRes()
        for k in NotResDic.keys():
            self.NotLoadedRes(resName=NotResDic[k])

    def setResNotAvail(self):
        
        resReq = self.ReqRes()
        resAvail = self.ResAvail()
        notAvail = [req for req in resReq.keys() if req not in resAvail.keys()]
        for req in notAvail:
            rname = resReq[req]
            self.ResNotAvail(resName=rname )

    def mapResAvail(self):
        #DOMAIN ASSEMBLY RESOURCES
        for i, ass in enumerate(System.AppDomain.CurrentDomain.GetAssemblies()):
            resNames = None
            if not ass.IsDynamic and self.NotLoadedRes().keys():
                #ASSEMBLY RESOURCES
                resNames = list(ass.GetManifestResourceNames())
                if resNames:
                    for res in resNames:
                        if self.getCoreName(res) in self.NotLoadedRes().keys():
                            for reqres in self.ReqRes().keys():
                                if self.getCoreName(res) == reqres:
                                    ssize = None
                                    resStrm = None
                                    try:
                                        resStrm = ass.GetManifestResourceStream(res)
                                        ssize = int(resStrm.Capacity)/1024
                                    except Exception as exm:
                                        continue
                                    tmpfile = self.getTmpFile(ssize)
                                    self.LoadedRes(res)
                                    self.ResAvail(resName=res,
                                      srcType=self._srcType(ass),
                                      srcPath=self._srcPath(ass),
                                      AssName=ass.GetName().Name,
                                      ResStream=resStrm,
                                      ResStreamName=res,
                                      TmpFilePath=tmpfile)

        if self.verbose:
            print '\n\t  RESOURCE REPORT'
            print self.reportDic(self.LoadedRes(), 'Resources with Stream')
            print
            print self.reportDic(self.NotLoadedRes(), 'Dll.Resources Currently NotLoaded')
            print

        return

    def ReqDlls(self, dllList=None, coreName=None, srcPath=None, srcType=None):

        if not isinstance(self._ReqCoreAndDllNamesAndSrcPathAndType, dict):
            self._ReqCoreAndDllNamesAndSrcPathAndType = {}

        if not dllList and not coreName:
            return self._ReqCoreAndDllNamesAndSrcPathAndType

        if isinstance(dllList, (str,unicode)):
            core = self.getCoreName(dllList)
            self._ReqCoreAndDllNamesAndSrcPathAndType \
            .update({core:{'DLL':dllList}})

            if srcType:
                assert srcType in ['File', 'Memory', '' ], \
                    "srcType must be of type  = 'File' | 'Memory' | '' "
                self._ReqCoreAndDllNamesAndSrcPathAndType \
                    .update({coreName:{'Type': srcPath}})

            if srcPath:
                self._ReqCoreAndDllNamesAndSrcPathAndType \
                    .update({coreName:{'Src':srcType}})
            return

        if dllList and isinstance(dllList, list):
            for intdll in dllList:
                core = self.getCoreName(intdll)
                self._ReqCoreAndDllNamesAndSrcPathAndType  \
                .update({core:{'DLL':intdll, 'Type': None, 'Src': None}})
            return

        if not dllList and coreName and coreName in self.ReqDlls().keys():

            if srcType:
                assert srcType in ['File', 'Memory', '' ], \
                    "srcType must be of type  = 'File' | 'Memory' | '' "
                self._ReqCoreAndDllNamesAndSrcPathAndType \
                    .update({coreName:{'Type': srcPath}})

            if srcPath:
                self._ReqCoreAndDllNamesAndSrcPathAndType \
                    .update({coreName:{'Src':srcType}})

            return True

        if not dllList and coreName:
            raise SyntaxError
        
        raise SyntaxError

    def LoadedDlls(self, dllname=None):
        if not isinstance(self._LoadedCoreAndDllNames, dict):
            self._LoadedCoreAndDllNames = {}
        if dllname:
            core = self.getCoreName(dllname)
            self._LoadedCoreAndDllNames.update({core:dllname})
        elif not dllname:
            return self._LoadedCoreAndDllNames

    def NotLoadedDlls(self, dllname=None):
        if not isinstance(self._NotLoadedCoreAndDllNames, dict):
            self._NotLoadedCoreAndDllNames = {}
        if dllname:
            core = self.getCoreName(dllname)
            self._NotLoadedCoreAndDllNames.update({core:dllname})
        elif not dllname:
            return self._NotLoadedCoreAndDllNames

    def DllsNotAvail(self, dllname=None):
        if not isinstance(self._ReqDllCoreNotAvialible, dict):
            self._ReqDllCoreNotAvialible = {}
        if dllname:
            core = self.getCoreName(dllname)
            self._ReqDllCoreNotAvialible.update({core:dllname})
        elif not dllname:
            return self._ReqDllCoreNotAvialible

    def ResAvail(self, resName=None, srcType=None, srcPath=None, AssName=None,
                 coreName=None, ResStream=None, ResStreamName=None,
                 TmpFilePath=None, tmpFileStream=None):

        if not isinstance(self._ResourceCoreAvailibleAndSrcPathAndType, dict):
            self._ResourceCoreAvailibleAndSrcPathAndType = {}
        if not resName and not coreName:
            return self._ResourceCoreAvailibleAndSrcPathAndType

        if resName:
            coreName = self.getCoreName(resName)
            self._ResourceCoreAvailibleAndSrcPathAndType \
                .update({coreName:{'DLL':resName, 'Type': None, 'Src': None,
                               'AssName':None, 'ResStream':None,
                               'ResStreamName':None, 'TmpFilePath':None,
                               'tmpFileStream':None, 'FileStream':None}})

        elif not resName and coreName:
            if not self._ResourceCoreAvailibleAndSrcPathAndType[coreName]['DLL']:
                raise SyntaxError

        if srcType:
            self._ResourceCoreAvailibleAndSrcPathAndType[coreName].update({'Type':srcType})
        if srcPath:
            self._ResourceCoreAvailibleAndSrcPathAndType[coreName].update({'Src':srcPath})
        if AssName:
            self._ResourceCoreAvailibleAndSrcPathAndType[coreName].update({'AssName':AssName})
        if ResStream:
            self._ResourceCoreAvailibleAndSrcPathAndType[coreName].update({'ResStream':ResStream})
        if ResStreamName:
            self._ResourceCoreAvailibleAndSrcPathAndType[coreName].update({'ResStreamName':ResStreamName})
        if TmpFilePath:
            self._ResourceCoreAvailibleAndSrcPathAndType[coreName].update({'TmpFilePath':TmpFilePath})
        if tmpFileStream:
            self._ResourceCoreAvailibleAndSrcPathAndType[coreName].update({'tmpFileStream':tmpFileStream})
        return

        raise SyntaxError

    def ResNotAvail(self, resName=None):
        if not isinstance(self._ResourceCoreNotAvilible, dict):
            self._ResourceCoreNotAvilible = {}
        if resName:
            core = self.getCoreName(resName)
            self._ResourceCoreNotAvilible.update({core:resName})
        elif not resName:
            return self._ResourceCoreNotAvilible

    def ReqRes(self, resName=None):
        if not isinstance(self._ResourceReqCoreAndSrcPathAndType, dict):
            self._ResourceReqCoreAndSrcPathAndType = {}
        if resName:
            core = self.getCoreName(resName)
            self._ResourceReqCoreAndSrcPathAndType.update({core:resName})
        elif not resName:
            return self._ResourceReqCoreAndSrcPathAndType

    def LoadedRes(self, resName=None):
        if not isinstance(self._LoadedResourceCore, dict):
            self._LoadedResourceCore = {}
        if resName:
            core = self.getCoreName(resName)
            self._LoadedResourceCore.update({core:resName})
        elif not resName:
            return self._LoadedResourceCore

    def NotLoadedRes(self, resName=None):
        if not isinstance(self._NotLoadedResourceCore, dict):
            self._NotLoadedResourceCore = {}
        if resName:
            core = self.getCoreName(resName)
            self._NotLoadedResourceCore.update({core:resName})
        elif not resName:
            return self._NotLoadedResourceCore

    def MemStreamRes(self, key):
        
        if self.MemRes:
            self.MemRes.append(self.ResAvail()[key])
        else:
            self.MemRes = [self.ResAvail()[key]]

        FWD = self.MemRes[-1]['TmpFilePath']
        mstrmBuff = System.Array.CreateInstance(System.Byte,self.MemRes[-1]['ResStream'].Capacity)
        self.MemRes[-1]['ResStream'].Read(mstrmBuff, 0 ,mstrmBuff.Length)

        System.IO.File.WriteAllBytes(FWD, mstrmBuff)
        self.MemRes[-1]['ResStream'].Close()

        isFWD = System.IO.File.Exists(FWD)
        fw = None
        if isFWD:
            fw = System.IO.FileStream(FWD, System.IO.FileMode.Open,
                                      System.IO.FileAccess.Read)
            if not fw.CanRead:
                print 'Possible Fatal Error {}:\n\t - Check exe: - No Read Access' \
                    .format(FWD)
        else:
            print 'Possible Fatal Error {}:\n\t - Check exe: - No temp File Create' \
                    .format(FWD)
        if fw:
            self.MemRes[-1]['tmpFileStream'] = fw
            self.mb.DefineManifestResource("Dll." + key, fw,
                                           ResourceAttributes.Public)
            
            if self.verbose:
                print self.reportDic(self.ResAvail()[key],
                                     'Loading Memory Resource - ' + key)
            if key in self.NotLoadedRes().keys():
                self._NotLoadedResourceCore.pop(key)
            self.LoadedRes(key)

        return

    def MemStreamDll(self, dllFile):

        if self.MemDlls:
            self.MemDlls.append(dllFile)
        else:
            self.MemDlls = [dllFile]

        mstrmBuff = System.IO.File.ReadAllBytes(self.MemDlls[-1])

        if mstrmBuff:
            if self.MemDlls and self.MemBytes:
                self.MemBytes.append(mstrmBuff)
            else:
                self.MemBytes = [mstrmBuff]

        if self.MemStrm:
            self.MemStrm.append(System.IO.MemoryStream(self.MemBytes[-1].Length))
        else:
            self.MemStrm  = [System.IO.MemoryStream(self.MemBytes[-1].Length)]

        if self.MemStrm and self.MemBytes:
            self.MemStrm[-1].Write(self.MemBytes[-1], 0 , self.MemBytes[-1].Length)

        return

    def createTmpDirectory(self):
        TmpDir  = System.IO.Path.Combine(System.IO.Path.GetTempPath(),'ipbtmp')
        if not self.TmpDir or self.TmpDir !=TmpDir:
            self.TmpDir = TmpDir

        if System.IO.Directory.Exists(self.TmpDir):
            self.TmpDirInfo = None
            tmpFiles = None
            try:
                self.TmpDirInfo = System.IO.DirectoryInfo(self.TmpDir)
            except Exception as extmp:
                print(extmp)

            if self.TmpDirInfo:
                tmpFiles = list(self.TmpDirInfo.GetFiles('*.tmp'))
                if tmpFiles and self.verbose:
                    print 'Removing {} tmp files from tmp directory {}' \
                            .format(len(tmpFiles), self.TmpDir)

                for tmpf in tmpFiles:
                    try:
                        System.IO.File.Delete(tmpf.FullName)
                    except Exception as exd:
                        continue

            tmpFileLst = None
            try:
                tmpFileLst = System.IO.DirectoryInfo(self.TmpDir).GetFiles('*.tmp')
            except Exception:
                pass
            if tmpFileLst and self.verbose:
                print '\n\tLocked tmp files:'
                print ('\n\t {}'*len(tmpFileLst)).format(*tmpFileLst)
        else:
            System.IO.Directory.CreateDirectory(TmpDir)
        return

    def getTmpFile(self, msizekb):
        # 4/29/2018 Copyright 2018 - hdunn. Apache 2.0 licensed.
        #----- Internal Load -------
        msize = msizekb*1024
        CD = System.IO.Directory.GetCurrentDirectory()
        tmpdir = System.IO.Path.Combine(System.IO.Path.GetTempPath(),'ipbtmp')
        if System.IO.Directory.Exists(tmpdir):
            tmpFilePath = System.IO.Path.GetFileName(System.IO.Path.GetTempFileName())
            tmpfile = System.IO.Path.Combine(tmpdir,System.IO.Path.GetFileName(tmpFilePath))

        preferFwd = System.IO.Path.Combine(System.IO.Path.GetTempPath(), tmpfile)
        spcf =  System.Environment.SpecialFolder.Personal
        altFwd = System.IO.Path.Combine(System.Environment.GetFolderPath(spcf),
                                        System.IO.Path.GetFileName(tmpfile))
        try:
            System.IO.File.Exists(preferFwd)
            FWD = preferFwd
        except Exception:
            print('Error in FWD')
            FWD = altFwd

        UWD = System.IO.Path.Combine(CD, tmpfile)
        nonRootTmp = False
        if System.IO.Path.GetPathRoot(FWD) != System.IO.Path.GetPathRoot(CD):
            nonRootTmp = True
            FWD = UWD

        SIPG = System.IO.Path.GetPathRoot
        CDSpace = System.IO.DriveInfo(SIPG(CD)).AvailableFreeSpace
        FDSpace = System.IO.DriveInfo(SIPG(FWD)).AvailableFreeSpace
        CDType = System.IO.DriveInfo(SIPG(CD)).DriveType
        FDType = System.IO.DriveInfo(SIPG(FWD)).DriveType

        try:
            if nonRootTmp and str(CDType) == 'Removable' \
                and CDSpace < msize \
                and str(FDType) == 'Fixed' \
                and FDSpace > msize:
                FWD = preferFwd
        except Exception as exf:
            print('Error in Set')
            print(exf)

        return FWD

    def creatEmebedList(self):#OK
        self.embedDict = {}
        for a in System.AppDomain.CurrentDomain.GetAssemblies():
            n = AssemblyName(a.FullName)

            if not a.IsDynamic and not a.EntryPoint:
                if self.config.standalone:
                    if n.Name.StartsWith("IronPython") or \
                    n.Name in ['Microsoft.Dynamic', 'Microsoft.Scripting']:
                        self.embedDict[n] = a

                # hdunn 3/15/2018 any(n.Name in dlln for dlln in dllNames) or \ above
                if any(n.Name in dlln for dlln in self.dllNames):
                    self.embedDict[n] = a

                if self.config.libembed and 'StdLib' in n.Name:
                    self.embedDict[n] = a
        return

    def embedRefs(self, hFS):#OK
        fcnt = -1
        for name, assem in self.embedDict.iteritems():
            fcnt += 1

            if assem.Location and name.Name in self.NotLoadedDlls().keys():
                if self.verbose:
                    if self.NotLoadedDlls().keys():
                        print self.reportDic(self.NotLoadedDlls(), ' Currently Not Loaded Dlls')

                    print "\n\tEmbedding %s %s" % (name.Name, str(name.Version))
                    strloc = self._strPathReduce(str(assem.Location),length=75)
                    print '\tlocation: ' + strloc

                if System.IO.File.Exists(assem.Location):

                    hFS.fdic('f' + str(fcnt), 'Stream', System.IO.FileStream(assem.Location,
                             System.IO.FileMode.Open,
                             System.IO.FileAccess.Read))
                    hFS.fdic('f' + str(fcnt), 'Name', name.Name)

                    shrtPath = self._strPathReduce(hFS.fdic()['f' + str(fcnt)]['Stream'].Name, length=20)
                    hFS.handles.append([name.Name, shrtPath,
                                 hFS.fdic()['f' + str(fcnt)]['Stream'].Handle])

                    if self.verbose: print '\tDefined Resource ' + str("Dll." + name.Name)
                    
                    self.mb.DefineManifestResource("Dll." + name.Name,
                                                        hFS.fdic()['f' + str(fcnt)]['Stream'],
                                                        ResourceAttributes.Public)
                    hFS.closes([name.Name, hFS.fdic()['f' + str(fcnt)]['Stream'].Handle])

                    if self.NotLoadedDlls().keys():
                        self.LoadedDlls("Dll." + name.Name)
                        self._NotLoadedCoreAndDllNames.pop(name.Name)
                        
                    if self.verbose: print '\n\tLoading ' + name.Name
                        
                    if self.NotLoadedDlls():
                        for intdll in self.NotLoadedDlls().keys():
                            if  name.Name == intdll:
                                self._NotLoadedCoreAndDllNames.pop(intdll)

            else:
                core = assem.GetName().Name.ToString()
                if core and core in self.NotLoadedDlls().keys():
                    self.DllsNotAvail('Dll.' + core)
                    self.NotLoadedDlls('Dll.' + core)

        if self.MemDlls:

            for i , memdll in enumerate(self.MemDlls):
                f_memLoaded = False
                memdllBase = None

                for intdll in self.NotLoadedDlls().keys():
                    memdllBase = System.IO.Path.GetFileName(self.getCoreName(memdll))
                    intdllBase = System.IO.Path.GetFileName(intdll)
                    if  memdllBase == intdllBase and self.MemDlls[i] == memdll:
                        f_memLoaded = True
                        if self.verbose:print '\n\tLoading Mem dll:\n\t {}'.format(memdll)
                        self.mb.DefineManifestResource("Dll." + memdllBase,
                                                            self.MemStrm[i],
                                                            ResourceAttributes.Public)
                        self.MemIdxToClose.append(i)

                        if intdll in self.NotLoadedDlls().keys():
                            self._NotLoadedCoreAndDllNames.pop(intdll)

                        if self.verbose:
                            print "\n\tEmbedding %s %s" % (System.IO.Path.GetFileName(memdll), '')
                            print '\tlocation: memory-backed resource'
                            print

                if f_memLoaded:
                    break

        if self.verbose:

            if self.NotLoadedDlls().keys():
                print self.reportDic(self.NotLoadedDlls(), 'Not Loaded Dlls')

            if not self.NotLoadedDlls().keys():
                print '\n\t All Required Dlls Loaded'

            if self.ResNotAvail().keys() and self.NotLoadedDlls().keys():
                print self.reportDic(self.ResNotAvail(), 'ResNotAvail:')

            if self.DllsNotAvail().keys() and self.NotLoadedDlls().keys():
                print self.reportDic(self.DllsNotAvail(), 'DllsNotAvail:')

        return hFS

    def setDllRefs(self): #OK

        if self.config.embed and self.config.dlls: #standalone is from pre-loaded AddRefs
            self.config.dlls = list(set(self.config.dlls))

            opath = System.IO.Path.GetDirectoryName(self.config.output)
            for dll in self.config.dlls:
                dpath = System.IO.Path.GetFileName(dll)
                if self.config.output  + 'DLL.dll' == dll:
                    self.dllNames.append(dpath)
                    self.MemStreamDll(self.config.output +'DLL.dll')
                    continue

                self.dllNames.append(dpath)
                #Dead Code maybe unless not embed??/---------------------------
                lpath = System.IO.Path.Combine(opath,dpath)
                if '.dll' not in dll:
                    print 'Not Dead'
                    try:
                        print 'Adding to Ref: ' + lpath
                        clr.AddReferenceToFileAndPath(lpath)
                    except Exception as exa:
                        msg = ('File | Filepath: \n {}: ' +
                               'not a DLL file or does not exist.').format(dll)
                        raise IOError(str(exa) + '\n' + msg)
                #------------------------------------------
                elif '.dll' in dll:
                    try:
                        print 'Adding .dll to Ref: ' + dll
                        clr.AddReferenceToFileAndPath(dll)
                    except Exception as exb:
                        msg = ('File | Filepath: \n {}: ' +
                               'not a DLL file or does not exist.').format(dll)
                        raise IOError(str(exb) + '\n' + msg)

            for dll in self.dllNames:
                self.NotLoadedDlls(dll)

        outdir = System.IO.Path.GetDirectoryName(self.config.output)
        if self.config.libembed:
            StdLibOutPath = System.IO.Path.Combine(outdir,'StdLib.dll')
            clrHasStdLib = False
            for clrRef in clr.References:
                if 'StdLib' in str(clrRef):
                    clrHasStdLib = True
            # error if already so try
            if System.IO.File.Exists(StdLibOutPath) and not clrHasStdLib:
                try:
                    clr.AddReferenceToFileAndPath(StdLibOutPath)
                    clrHasStdLib = True
                except(System.IO.IOException, System.IO.FileLoadException) as exd:
                    print('Error in StdLib Load')
                    if exd.GetType()==System.IO.IOException:
                        msg = ('File | Filepath:\nStdLib.dll or {}:\n ' +
                               'Not a DLL file or does not exist.') \
                               .format(StdLibOutPath)
                        print msg
                    elif exd.GetType()==System.IO.FileLoadException:
                        msg = ('File | Filepath: {}\n' +
                              'Not a clr Loadable file.') \
                              .format(StdLibOutPath)
                        print msg

            if not clrHasStdLib:
                try:
                    clr.AddReference("StdLib.dll")
                except (System.IO.IOException, System.IO.FileLoadException) as ex:
                    print('Error in clrhasStdLib')
                    if ex.GetType()==System.IO.IOException:
                        msg = ('File | Filepath:\nStdLib.dll or "StdLib.dll":\n ' +
                               'Not a DLL file or does not exist.')
                        print msg
                    elif ex.GetType()==System.IO.FileLoadException:
                        msg = ('File | Filepath: "StdLib.dll"\n' +
                              'Not a clr Loadable file.')
                        print msg
                if self.verbose:
                    print
                    print 'Trying to finish .... - check compiled function, paths and access'
                    print

        if self.MemDlls and self.verbose:
            print '\n\tMemory Dlls:'
            print ('\n\t{}'*len(self.MemDlls)).format(*self.MemDlls)
            print

        return

    def updateResCurrent(self):

        if self.LoadedRes().keys() and self.ResAvail().keys():
            for res in self.ResAvail().keys():
                if res in self.LoadedRes().keys():
                    key = [rescore for rescore in self.ResAvail().keys() \
                           if rescore == res]
                    if key:
                        key = key[0]
                        self.MemStreamRes(key)

        if self.verbose:
            if (self.NotLoadedDlls().keys() or self.NotLoadedRes().keys) and self.ResNotAvail().keys():
                nAvail = [res for res in self.NotLoadedRes().keys() if res in self.ResNotAvail().keys()]
                if nAvail:
                    print
                    print '\tCannot find/load the following required dlls or resources:'
                    print self.reportDic(self.NotLoadedDlls(), 'Resource/Dlls Not Loaded')
                    print self.reportDDic(self.ResAvail(), 'Internal Resouces Availible')
                    print
                    print '\tWill not be able to load:'
                    for nar in nAvail:
                        print '\t' + str(nar)
                    print
                    print '\tTry the compiled executable (exe) {}:\n' + \
                          '\t  - Check that the unloaded resources are required. -'
                    print       
        print
        return True

    def reportDDic(self, DDic, strTitle):
        '''
          Nested dict print
          DDic is for double (nested dics)

          :param: DDic [dict] is return from PyDynAssem instance - i.e. pydynassem.ReqDlls()
              strTitle [str] - title caption

        '''

        rpt = '\n\t' + strTitle + ':'
        if DDic and DDic.keys():
            for k in DDic.keys():
                rpt = rpt + '\n\t{}'.format(k)
                for a, n in DDic[k].iteritems():
                    rpt = rpt +  '\n\t  {} - {}'.format(a, n)
        else:
            rpt = '\n\tEmpty: ' + strTitle
        return rpt

    def reportDic(self, Dic, strTitle):
        '''
          Dict print
          Dic is for single (normal dics)

          :param: Dic [dict] is return from PyDynAssem instance - i.e. pydynassem.NotLoadedDlls()
              strTitle [str] - title caption

        '''

        rpt = '\n\t' + strTitle + ':'
        
        if Dic and Dic.keys():
            for k, v in Dic.iteritems():
                rpt = rpt + '\n\t  {} - {}'.format(k, v)
        else:
            rpt = '\n\tEmpty: ' + strTitle
        return rpt

    def getCoreName(self,  dllName):

        core = dllName.replace('Dll.','').replace('IPDll.','').replace('.dll','')
        return core

    def _srcType(self, ass):

        assemLoc = None
        try:
            assemLoc = ass.Location
        except Exception:
            pass
        if assemLoc and System.IO.Directory.Exists(System.IO.Path.GetDirectoryName(assemLoc)):
            return 'File'
        else:
            return 'Memory'

    def _srcPath(self, ass):

        assemLoc = None
        try:
            assemLoc = ass.Location
        except Exception:
            pass
        if assemLoc:
            return assemLoc
        else:
            return ass.GetName().Name + '-Internal'

    def _strPathReduce(self, path, length=90):
        # Needs clr, System
        if path and len(path) <= length:
            return path
        elif not path:
            return ''
        strloc = path
        cutto = length
        strdrv = ''
        strloc_ = strloc
        slashidx = [len(strloc)//2]
        strdrv = System.IO.Path.GetPathRoot(strloc)
        if strdrv and len(strdrv) != 0:
            strloc_ = strloc.replace(strdrv,'')
        if '\\' in strloc:
            slashidx = (i for i, ch in enumerate(strloc) if ch == '\\')
        elif '/' in strloc:
            slashidx = (i for i, ch in enumerate(strloc) if ch == '/')
        else: return strloc
        cnt = 0
        while cnt < 25 and (slashidx and len(strloc_) > cutto):
            #        print 'cnt ' + str(cnt)
            try:
                strloc_ = strloc[slashidx.next():]
            except StopIteration:
               break
            cnt += 1

        strloc = strdrv + '...' + strloc_

        return strloc
    
def GenerateExe(config):
    """ 
      Generates the stub .EXE file for starting the app
      
      For an ipybuilder.exe build - Must set <proj>assembly.json flag:
      stanalone: "true" - if IronPython is not installed in loadable path.
      
      ipybuilde.exe will automatically embed dlls into standalone if IronPython
      is not found.
      
      see Documentation 
      
    """
    clrRefs = []
    for clrRef in list(clr.References):
        ref = clr.Convert(clrRef, System.Reflection.Assembly)
        clrRefs.append(ref.GetName())
    
    if config.verbose: print 'Checking IP - use the -find flag if system IP has changed'
    
    #backup check should have caught this in buildmake.py
    if clrRefs and not config.standalone and \
        str(sys.argv[0]).find('ipybuilder.exe') != -1:

            if not any(clref.ToString().find('IronPython') != -1 for clref in clrRefs):
                config.standalone = True
                print 'WARN - switched to stanalone - No IronPython detected'

    if config.standalone:
        config.embed = True
    
    pyDynAssm =  PythonDynamic(config,
                               AssemblyName(System.IO.FileInfo(config.output).Name),
                               list(internalDlls))
    pyDynAssm.dllNames = []
    if config.verbose: print 'pyDynAssm setup'
    if config.file_version is not None:
        pyDynAssm.Name.Version = Version(config.file_version)
    hFS = hndlFileStreams()
    if config.verbose: print 'hFS setup'
    assemblyResolveMethod = None
    # 3/19/2018-5/62018  # Copyright 2018 - hdunn. Apache 2.0 licensed. Modified from original.
    # --- handle dll and StdLib embed -----------
#    embedDict = None
    if config.verbose: print 'config.embed = ' + str(config.embed)
    if config.embed:
        if config.verbose: print 'Passed into embed'
        pyDynAssm.setDllRefs()
        if config.verbose: print 'Passed setDllRefs'
        pyDynAssm.creatEmebedList()
        if config.verbose: print 'Passed creatEmebedList'
        hFS = pyDynAssm.embedRefs(hFS)
        if config.verbose: print '\nPassed embedRefs'
        pyDynAssm.updateResCurrent()

        if config.verbose and (pyDynAssm.NotLoadedDlls().keys() or pyDynAssm.NotLoadedRes().keys()):
            print pyDynAssm.reportDDic(pyDynAssm.ReqDlls(), 'ReqDlls')
            print pyDynAssm.reportDDic(pyDynAssm.ResAvail(), 'ResAvail')
            print pyDynAssm.reportDic(pyDynAssm.ReqRes(), 'ReqResources')
            print pyDynAssm.reportDic(pyDynAssm.ResNotAvail(), 'ResNotAvail')

        print 'Continuing ...'
        assemblyResolveMethod = None

        # we currently do no error checking on what is passed in to the AssemblyResolve event handler
        assemblyResolveMethod = pyDynAssm.tb.DefineMethod("AssemblyResolve", MethodAttributes.Public | MethodAttributes.Static, clr.GetClrType(Assembly), (clr.GetClrType(System.Object), clr.GetClrType(System.ResolveEventArgs)))
        gen = assemblyResolveMethod.GetILGenerator()
        s = gen.DeclareLocal(clr.GetClrType(System.IO.Stream)) # resource stream
        gen.Emit(OpCodes.Ldnull)
        gen.Emit(OpCodes.Stloc, s)
        d = gen.DeclareLocal(clr.GetClrType(System.Array[System.Byte])) # data buffer
        gen.EmitCall(OpCodes.Call, clr.GetClrType(Assembly).GetMethod("GetEntryAssembly"), ())
        gen.Emit(OpCodes.Ldstr, "Dll.")
        gen.Emit(OpCodes.Ldarg_1)    # The event args
        gen.EmitCall(OpCodes.Callvirt, clr.GetClrType(System.ResolveEventArgs).GetMethod("get_Name"), ())
        gen.Emit(OpCodes.Newobj, clr.GetClrType(AssemblyName).GetConstructor((str, )))
        gen.EmitCall(OpCodes.Call, clr.GetClrType(AssemblyName).GetMethod("get_Name"), ())
        gen.EmitCall(OpCodes.Call, clr.GetClrType(str).GetMethod("Concat", (str, str)), ())
        gen.EmitCall(OpCodes.Callvirt, clr.GetClrType(Assembly).GetMethod("GetManifestResourceStream", (str, )), ())
        gen.Emit(OpCodes.Stloc, s)
        gen.Emit(OpCodes.Ldloc, s)
        gen.EmitCall(OpCodes.Callvirt, clr.GetClrType(System.IO.Stream).GetMethod("get_Length"), ())
        gen.Emit(OpCodes.Newarr, clr.GetClrType(System.Byte))
        gen.Emit(OpCodes.Stloc, d)
        gen.Emit(OpCodes.Ldloc, s)
        gen.Emit(OpCodes.Ldloc, d)
        gen.Emit(OpCodes.Ldc_I4_0)
        gen.Emit(OpCodes.Ldloc, s)
        gen.EmitCall(OpCodes.Callvirt, clr.GetClrType(System.IO.Stream).GetMethod("get_Length"), ())
        gen.Emit(OpCodes.Conv_I4)
        gen.EmitCall(OpCodes.Callvirt, clr.GetClrType(System.IO.Stream).GetMethod("Read", (clr.GetClrType(System.Array[System.Byte]), int, int)), ())
        gen.Emit(OpCodes.Pop)
        gen.Emit(OpCodes.Ldloc, d)
        gen.EmitCall(OpCodes.Call, clr.GetClrType(Assembly).GetMethod("Load", (clr.GetClrType(System.Array[System.Byte]), )), ())
        gen.Emit(OpCodes.Ret)

        # generate a static constructor to assign the AssemblyResolve handler (otherwise it tries to use IronPython before it adds the handler)
        # the other way of handling this would be to move the call to InitializeModule into a separate method.
        staticConstructor = pyDynAssm.tb.DefineConstructor(MethodAttributes.Public | MethodAttributes.Static, CallingConventions.Standard, System.Type.EmptyTypes)
        gen = staticConstructor.GetILGenerator()
        gen.EmitCall(OpCodes.Call, clr.GetClrType(System.AppDomain).GetMethod("get_CurrentDomain"), ())
        gen.Emit(OpCodes.Ldnull)
        gen.Emit(OpCodes.Ldftn, assemblyResolveMethod)
        gen.Emit(OpCodes.Newobj, clr.GetClrType(System.ResolveEventHandler).GetConstructor((clr.GetClrType(System.Object), clr.GetClrType(System.IntPtr))))
        gen.EmitCall(OpCodes.Callvirt, clr.GetClrType(System.AppDomain).GetMethod("add_AssemblyResolve"), ())
        gen.Emit(OpCodes.Ret)

    mainMethod = pyDynAssm.tb.DefineMethod("Main", MethodAttributes.Public | MethodAttributes.Static, int, ())
    if config.target == System.Reflection.Emit.PEFileKinds.WindowApplication and config.mta:
        mainMethod.SetCustomAttribute(clr.GetClrType(System.MTAThreadAttribute).GetConstructor(()), System.Array[System.Byte](()))
    elif config.target == System.Reflection.Emit.PEFileKinds.WindowApplication:
        mainMethod.SetCustomAttribute(clr.GetClrType(System.STAThreadAttribute).GetConstructor(()), System.Array[System.Byte](()))

    gen = mainMethod.GetILGenerator()
    mstream = None
    # get the ScriptCode assembly...
    if config.embed:

        # print 'sys argv ' + str(sys.argv[0])
        # put the generated DLL into the resources for the stub exe
        w = pyDynAssm.mb.DefineResource("IPDll.resources", "Embedded IronPython Generated DLL")
        # print 'IPDLL NAME: ' + 'IPDLL.' + config.output
        # 4/4/2018 Copyright 2018 - hdunn. Apache 2.0 licensed. Modified from original.----- IPDLL NAME
        strPathRefIPDll = System.IO.DirectoryInfo(config.output).Name
        # print 'strPathRefIPDll ' + str(strPathRefIPDll)
        #---  'Changed to: ' + "IPDll." + strPathRefIPDll
        # comment out System.IO.File.Exists(config.output + ".dll"))
        # w.AddResource("IPDll." + config.output, System.IO.File.ReadAllBytes(config.output + ".IPDLL"))
        # 5/4/2018 Copyright 2018 - hdunn. Apache 2.0 licensed. Modified from original.-----
        
        try:
            mstream = System.IO.MemoryStream(System.IO.File.ReadAllBytes(config.output + ".dll"))
        except Exception as exs:
            print 'Err in mstream'
            print(exs)
        if mstream:
            mstream.Close()
        w.AddResource("IPDll." + strPathRefIPDll, mstream.ToArray())
        #w.AddResource("IPDll." + strPathRefIPDll, mstreamBuff)
        ## typo fix 5/4/18
        #w.AddResource("IPDll." + strPathRefIPDll, System.IO.File.ReadAllBytes(config.output + ".dll"))
        #--------------------
        # generate code to load the resource
        gen.Emit(OpCodes.Ldstr, "IPDll")
        gen.EmitCall(OpCodes.Call, clr.GetClrType(Assembly).GetMethod("GetEntryAssembly"), ())
        gen.Emit(OpCodes.Newobj, clr.GetClrType(System.Resources.ResourceManager).GetConstructor((str, clr.GetClrType(Assembly))))
        # ---- hdunn dido --------
        gen.Emit(OpCodes.Ldstr, "IPDll." + strPathRefIPDll)#strPathRefIPDll)#config.output 4/4
        # ------------------
        gen.EmitCall(OpCodes.Call, clr.GetClrType(System.Resources.ResourceManager).GetMethod("GetObject", (str, )), ())
        gen.EmitCall(OpCodes.Call, clr.GetClrType(System.Reflection.Assembly).GetMethod("Load", (clr.GetClrType(System.Array[System.Byte]), )), ())
        if config.verbose: print 'Base embed... completed {}'.format(config.output + ".dll")

    else:

        if config.verbose: print 'No embed'
        # variables for saving original working directory und return code of script
        wdSave = gen.DeclareLocal(str)

        # save current working directory
        gen.EmitCall(OpCodes.Call, clr.GetClrType(System.Environment).GetMethod("get_CurrentDirectory"), ())
        gen.Emit(OpCodes.Stloc, wdSave)
        gen.EmitCall(OpCodes.Call, clr.GetClrType(Assembly).GetMethod("GetEntryAssembly"), ())
        gen.EmitCall(OpCodes.Callvirt, clr.GetClrType(Assembly).GetMethod("get_Location"), ())
        gen.Emit(OpCodes.Newobj, clr.GetClrType(System.IO.FileInfo).GetConstructor((str, )))
        gen.EmitCall(OpCodes.Call, clr.GetClrType(System.IO.FileInfo).GetMethod("get_Directory"), ())
        gen.EmitCall(OpCodes.Call, clr.GetClrType(System.IO.DirectoryInfo).GetMethod("get_FullName"), ())
        gen.EmitCall(OpCodes.Call, clr.GetClrType(System.Environment).GetMethod("set_CurrentDirectory"), ())
        # 4.11.2018 Copyright 2018 - hdunn. Apache 2.0 licensed. Modified from original.
        strPathRefDll = System.IO.DirectoryInfo(config.output).Name + '.dll'
        gen.Emit(OpCodes.Ldstr, strPathRefDll)
        gen.EmitCall(OpCodes.Call, clr.GetClrType(System.IO.Path).GetMethod("GetFullPath", (clr.GetClrType(str), )), ())
        # result of GetFullPath stays on the stack during the restore of the
        # original working directory
        # restore original working directory
        gen.Emit(OpCodes.Ldloc, wdSave)
        gen.EmitCall(OpCodes.Call, clr.GetClrType(System.Environment).GetMethod("set_CurrentDirectory"), ())

        # for the LoadFile() call, the full path of the assembly is still is on the stack
        # as the result from the call to GetFullPath()
        gen.EmitCall(OpCodes.Call, clr.GetClrType(System.Reflection.Assembly).GetMethod("LoadFile", (clr.GetClrType(str), )), ())

    # emit module name
    if config.verbose: print 'emit main ... '
    gen.Emit(OpCodes.Ldstr, "__main__")  # main module name
    gen.Emit(OpCodes.Ldnull)             # no references
    gen.Emit(OpCodes.Ldc_I4_0)           # don't ignore environment variables for engine startup

    # call InitializeModule
    # (this will also run the script)
    # -------------------------------------
    # 3.10.2018 Copyright 2018 - hdunn. Apache 2.0 licensed. Modified from original.
    Init_Long = None
    for mi in clr.GetClrType(PythonOps).GetMethods():
        if "InitializeModuleEx" in mi.Name and len(mi.GetParameters()) == 4:
            Init_Long = mi

    gen.EmitCall(OpCodes.Call, Init_Long, ())
    # -------------------------------------
    gen.Emit(OpCodes.Ret)
    pyDynAssm.tb.CreateType()
    pyDynAssm.ab.SetEntryPoint(mainMethod, config.target)
    pyDynAssm.ab.Save(pyDynAssm.Name.Name + ".exe", config.platform, config.machine)
    if mstream:
        del mstream

    if pyDynAssm.MemRes:
        for dic in pyDynAssm.MemRes:
            if 'tmpFileStream' in dic.keys():
                dic['tmpFileStream'].Close()

    pyDynAssm.createTmpDirectory()#DELETES TMPFILES/Creates dir only, if not exist

    if config.verbose:
        print 'Gen emit ... done'
        print "Save as " +  pyDynAssm.Name.Name + ".exe"

        print pyDynAssm.reportDic(pyDynAssm.LoadedDlls(), 'Loaded Dlls')
        print pyDynAssm.reportDic(pyDynAssm.NotLoadedDlls(),'Not Loaded Dlls')
        print pyDynAssm.reportDic(pyDynAssm.LoadedRes(), 'Loaded Resources')
        if any(key not in pyDynAssm.LoadedDlls().keys() for key in pyDynAssm.ReqDlls().keys()):
            print pyDynAssm.reportDic(pyDynAssm.ResNotAvail(), 'ResNotAvail')

        print str(hFS.hndlReport())
        print
        print str(hFS.hndlReport(typ='closed'))
        print

        clrRefs = []
        for clrRef in list(clr.References):
            ref = clr.Convert(clrRef, System.Reflection.Assembly)
            clrRefs.append(ref.GetName())
        
        print '\nclr References:'
        print ('\n\t{}'*len(clrRefs)).format(*clrRefs)
        print

    if pyDynAssm.MemDlls:
        for idx in pyDynAssm.MemIdxToClose:
            if config.verbose:
                print 'Closing MemStrm: ' \
                      + System.IO.Path.GetFileName(pyDynAssm.MemDlls[idx])
            pyDynAssm.MemStrm[idx].Close()
    if System.IO.File.Exists(config.output + ".IPDLL"):
        try:
            System.IO.File.Delete(config.output + ".IPDLL")
        except Exception as exdl:
            print 'del <{}>.IPDLL'.format(config.output)
            print(exdl)

class Config(object):

    def __init__(self):
        self.output = None
        self.main = None
        self.main_name = None
        self.target = System.Reflection.Emit.PEFileKinds.Dll
        self.embed = False
        self.libembed = False
        self.standalone = False
        self.mta = False
        self.platform = System.Reflection.PortableExecutableKinds.ILOnly
        self.machine = System.Reflection.ImageFileMachine.I386
        self.files = []
        self.file_info_product = None
        self.file_info_product_version = None
        self.file_info_company = None
        self.file_info_copyright = None
        self.file_info_trademark = None
        self.file_version = None
        self.dlls = []
        self.verbose = False

    def ParseArgs(self, args, respFiles=[]):
        for arg in args:
            arg = arg.strip()
            #hdunn 3/12/2018 ------------
            if '"' in arg and "'" in arg:
                arg = arg.replace("'", "")
                arg = arg.replace('"', '')
            # ---------------------------
            if arg.startswith("#"):
                continue

            if arg.startswith("/main:"):
                self.main_name = self.main = arg[6:]
                # only override the target kind if its current a DLL
                if self.target == System.Reflection.Emit.PEFileKinds.Dll:
                    self.target = System.Reflection.Emit.PEFileKinds.ConsoleApplication

            elif arg.startswith("/out:"):
                self.output = arg[5:]

            elif arg.startswith("/target:"):
                tgt = arg[8:]
                if tgt == "exe": self.target = System.Reflection.Emit.PEFileKinds.ConsoleApplication
                elif tgt == "winexe": self.target = System.Reflection.Emit.PEFileKinds.WindowApplication
                else: self.target = System.Reflection.Emit.PEFileKinds.Dll

            elif arg.startswith("/platform:"):
                pform = arg[10:]
                if pform == "x86":
                    self.platform = System.Reflection.PortableExecutableKinds.ILOnly | System.Reflection.PortableExecutableKinds.Required32Bit
                    self.machine  = System.Reflection.ImageFileMachine.I386
                elif pform == "x64":
                    self.platform = System.Reflection.PortableExecutableKinds.ILOnly | System.Reflection.PortableExecutableKinds.PE32Plus
                    self.machine  = System.Reflection.ImageFileMachine.AMD64
                else:
                    self.platform = System.Reflection.PortableExecutableKinds.ILOnly
                    self.machine  = System.Reflection.ImageFileMachine.I386

            elif arg.startswith("/file_info_product:"):
                self.file_info_product = arg[19:]
            elif arg.startswith("/file_info_product_version:"):
                self.file_info_product_version = arg[27:]
            elif arg.startswith("/file_info_company:"):
                self.file_info_company = arg[19:]
            elif arg.startswith("/file_info_copyright:"):
                self.file_info_copyright = arg[21:]
            elif arg.startswith("/file_info_trademark:"):
                self.file_info_trademark = arg[21:]
            elif arg.startswith("/file_version:"):
                validVer = ["1","2","3","4","5","6","7","8","9","0","."]
                assert all(ch in validVer for ch in arg[14:]), \
                    'bad file_version format not like "0.100.2.3000"'
                self.file_version = arg[14:]

            elif arg.startswith("/embed"):
                self.embed = True
             #hdunn 3/19/2018 ------------
            elif arg.startswith("/libembed"):
                self.libembed = True
            elif arg.startswith("/standalone"):
                self.standalone = True

            elif arg.startswith("/mta"):
                self.mta = True
             #hdunn 3/19/2018 ------------
            elif arg.endswith(".dll"):
                self.dlls.append(arg)
            #hdunn 4/8/2018 ------------
            elif arg in ["-v"]:
                self.verbose = True
            elif arg in ["/?", "-?", "/h", "-h"]:
                print __doc__
                sys.exit(0)

            else:
                if arg.startswith("@"):
                    respFile = System.IO.Path.GetFullPath(arg[1:])
                    if not respFile in respFiles:
                        respFiles.append(respFile)
                        with open(respFile, 'r') as f:
                           self.ParseArgs(f.readlines(), respFiles)
                    else:
                        print "WARNING: Already parsed response file '%s'\n" % arg[1:]
                else:
                    #adding py files here
                    self.files.append(arg)

    #hdunn 4/2/2018 ----------
    def Validate(self, config):
        if self.main_name:
            if config.verbose: print 'validate main name ' + str(self.main_name)
        #  self.main_name or tobe or not tobe
        if self.main and '.py' in self.main and self.main not in self.files:
            self.files.append(self.main)
        if not self.files and not self.main_name:
            print "No files or main defined"
            return False
        #------------------------------
        if self.files:
            cpyfiles = list(self.files)
            for fl in cpyfiles:
                if '.py' not in fl:
                    self.files.remove(fl)
        #-------------------------------
        if self.target != System.Reflection.Emit.PEFileKinds.Dll and self.main_name == None:
            print "EXEs require /main:<filename> to be specified"
            return False

        if not self.output and self.main_name:
            self.output = System.IO.Path.GetFileNameWithoutExtension(self.main_name)
        elif not self.output and self.files:
            self.output = System.IO.Path.GetFileNameWithoutExtension(self.files[0])
        if config.verbose: print 'First: output path... done'
        return True

    def __repr__(self):
        res = "Input Files:\n"
        for afile in self.files:
            if afile:
                res += "\t%s\n" % afile

        res += "Output:\n\t%s\n" % self.output
        res += "Target:\n\t%s\n" % self.target
        res += "Platform:\n\t%s\n" % self.platform
        res += "Machine:\n\t%s\n" % self.machine

        if self.target == System.Reflection.Emit.PEFileKinds.WindowApplication:
            res += "Threading:\n"
            if self.mta:
                res += "\tMTA\n"
            else:
                res += "\tSTA\n"
        return res

def Main(args):

    config = Config()

    config.ParseArgs(args)
    if not config.Validate(config):
        print __doc__
        sys.exit(0)

    if config.verbose:
            res = ''
            print 'Compiling with config:\n'
            if 'StdLib' in config.output:
                res = "Input Files - see:{}\n" \
                .format(config.output + '.txt')
            else:
                res += "Input Files - see below 'Setting up compile' output\n"

            res += "Output:\n\t%s\n" % config.output
            res += "Target:\n\t%s\n" % config.target
            res += "Platform:\n\t%s\n" % config.platform
            res += "Machine:\n\t%s\n" % config.machine

            if config.target == System.Reflection.Emit.PEFileKinds.WindowApplication:
                res += "Threading:\n"
                if config.mta:
                    res += "\tMTA\n"
                else:
                    res += "\tSTA\n"
            print res

    #hdunn 4/3/2018 -try clr.CompileMods
    msg = ''
    pre = ''
    if config.verbose:
        print "Setting up full compile: "
        pre = '\nSending internal to clr.ComplierModules:\n'
        msg = msg + '\tconifg.ouput is: {}\n'.format(config.output)
        msg = msg + '\tconfig.main_name is: {}\n'.format(config.main_name)

    if config.files and config.verbose:
        #hdunn 4/6/2018 output ----------
        if 'StdLib' in config.output:
            cfiles = list(config.files)
            cfiles.sort()
            with open( config.output + '.txt', 'w') as tw:
                tw.writelines(('\n').join(cfiles))
        elif config.files:
            msg = msg + ('\tconfig.files:\n\t' + '{} \n\t'*len(config.files)) \
                            .format(*config.files)
            print 'config.files len: ' + str(len(config.files))

    if config.dlls and config.verbose and not 'StdLib' in config.output:
        msg = msg + ('\n\n\tproject config.dlls (no re-compile):\n\t' + \
                     '{} \n\t'*len(config.dlls)).format(*config.dlls)
        print 'config.dlls len: ' + str(len(config.dlls))

    elif config.verbose and not config.files and not config.dlls:
        msg = msg + '\nconfig.files and config.dlls are empty:'

    print str(pre + msg)
    #hdunn 4/6/2018 Try ----------
    try:
        if config.verbose:
            print 'Compiling dlls ...'
            print ' main name - ' + str(config.main_name)
        clr.CompileModules(config.output + ".dll",
                           mainModule = config.main_name,
                           *config.files)
    except Exception as ex:
        pre = ('FATAL ERROR - Internal clr.ComplierModules:' + \
              '\n    - possible bad file in config.files:' + \
              '\n    - This Error will cause additional Errors:' + \
              '\n    - Err like:\n {} - acces denied or does not exist.').format(config.output + '.dll')
        
        print(str(ex)[:255] + ' ...' + '\n' + pre + msg)

    if config.target != System.Reflection.Emit.PEFileKinds.Dll:
        print 'Gen Start at - ' + str(time.ctime())
        GenerateExe(config)
        print 'Done generating exe ...'
        #pyc Always has file access SO MOVED/COPY In BUILDMAKE

        
    elif config.target == System.Reflection.Emit.PEFileKinds.Dll:
        if config.verbose: print "\tSaved Lib (exe or dll) as: {}" \
                                 .format(config.output + '.dll')
                                 
    return True

if __name__ == "__main__":
    try:
        Main(sys.argv[1:])
    except Exception as ex:
        print('Error in Main:')
        print(ex)
