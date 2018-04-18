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
# Modification not endorsed by Microsoft Corp. or Secret Labs AB
# 
# You must not remove this notice, or any other, from this software.
#
#####################################################################################

"""
    ::pyc: The Command-Line Python Compiler
    ::
    ::Usage: ipy.exe pyc.py [options] file [file ...]
    ::
    ::Options:
        /out:output_file                          Output file name (default is main_file.<extenstion>)
        /target:dll                               Compile only into dll.  Default
        /target:exe                               Generate console executable stub for startup in addition to dll.
        /target:winexe           TODO             Generate windows executable stub for startup in addition to dll.
        @<file>                  NOT TESTED       Specifies a response file to be parsed for input files and command line options (one per line)
        /file_version:<version>  NOT IMPLEMENTED  Set the file/assembly version
        /? /h                                     This message
        -v - in ipybuild args                     Verbose output
        
    ::EXE/WinEXE specific options:
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
    ::Example:
        ipy.exe pyc.py /main:Program.py Form.py /target:exe

"""
from version import __version__

import sys

try:
    import clr
    clr.AddReference("IronPython")
    clr.AddReference("System")
    from System.Collections.Generic import List
    import IronPython.Hosting as Hosting
    from IronPython.Runtime.Operations import PythonOps
    import System
    from System import IO
    from System import Version
    from System.Reflection import Emit, Assembly
    from System.Reflection.Emit import OpCodes, AssemblyBuilderAccess
    from System.Reflection import AssemblyName, TypeAttributes, MethodAttributes, ResourceAttributes, CallingConventions

except Exception as exi:
    print(exi)     

def GenerateExe(config):
    """generates the stub .EXE file for starting the app"""
    aName = AssemblyName(System.IO.FileInfo(config.output).Name)

    if config.file_version is not None:
        aName.Version = Version(config.file_version)

    ab = PythonOps.DefineDynamicAssembly(aName, AssemblyBuilderAccess.RunAndSave)
    ab.DefineVersionInfoResource(config.file_info_product,
                                 config.file_info_product_version,
                                 config.file_info_company,
                                 config.file_info_copyright,
                                 config.file_info_trademark)

    mb = ab.DefineDynamicModule(config.output, aName.Name + ".exe")
    tb = mb.DefineType("PythonMain", TypeAttributes.Public)
    assemblyResolveMethod = None
    # 3/19/2018  # Copyright 2018 - hdunn. Apache 2.0 licensed. Modified from original.
    # --- handle dll and StdLib embed -----------
    dllNames = []
    if config.embed and config.dlls: #not for standalone ?
        config.dlls = list(set(config.dlls))
        opath = System.IO.Path.GetDirectoryName(config.output)
        print 'opath: ' + opath
        for dll in config.dlls:
            dpath = System.IO.Path.GetFileName(dll)
            dllNames.append(dpath)
            lpath = System.IO.Path.Combine(opath,dpath)
            if '.dll' not in dll:
                try:
                    print 'Adding to Ref: ' + lpath
                    clr.AddReferenceToFileAndPath(lpath)
                except Exception as exa:
                    msg = ('File | Filepath: \n {}: ' + 
                           'not a DLL file or does not exist.').format(dll)
                    raise IOError(str(exa) + '\n' + msg)
                        
            elif '.dll' in dll:
                try:
                    print 'Adding .dll to Ref: ' + dll
                    clr.AddReferenceToFileAndPath(dll)
                except Exception as exb:
                    msg = ('File | Filepath: \n {}: ' + 
                           'not a DLL file or does not exist.').format(dll)
                    raise IOError(str(exb) + '\n' + msg)
            
    if config.standalone or config.libembed or config.embed:
        outdir = System.IO.Path.GetDirectoryName(config.output)
        StdLibOutPath = System.IO.Path.Combine(outdir,'StdLib.dll')
        print 'exists ' + str(System.IO.File.Exists(StdLibOutPath))
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
                try:
                    print str(exd.GetType().FullName) + '\n' + str(exd.Message)
                    print
                except Exception as exu:
                        raise exu
            
                if exd.GetType()==System.IO.IOException:    
                    msg = ('File | Filepath:\nStdLib.dll or {}:\n ' + 
                           'Not a DLL file or does not exist.') \
                           .format(config.output + '.dll')
                    print msg
                elif exd.GetType()==System.IO.FileLoadException:
                    msg = ('File | Filepath: {}\n' + 
                          'Not a clr Loadable file.') \
                          .format(config.output + '.dll')
                    print msg
        
        if not clrHasStdLib:
        
            try:
                clr.AddReference("StdLib.dll")
            except (System.IO.IOException, System.IO.FileLoadException) as ex:
                try:
                    print str(ex.GetType().FullName) + '\n' + str(ex.Message)
                    print
                except Exception as exu:
                        raise exu
            
                if ex.GetType()==System.IO.IOException:    
                    msg = ('File | Filepath:\nStdLib.dll or {}:\n ' + 
                           'Not a DLL file or does not exist.') \
                           .format(config.output + '.dll')
                    print msg
                elif ex.GetType()==System.IO.FileLoadException:
                    msg = ('File | Filepath: {}\n' + 
                          'Not a clr Loadable file.') \
                          .format(config.output + '.dll')
                    print msg
            print    
            print 'Trying to finish .... - check compiled function, paths and access'        
            print
        
        config.embed = True
        
        # 3/19/2018,4/3/2018  # Copyright 2018 - hdunn. Apache 2.0 licensed. Modified from original.
        # ----- handle dll and StdLib embed -----------
        embedDict = {}
        for a in System.AppDomain.CurrentDomain.GetAssemblies():
            n = AssemblyName(a.FullName)
            
            if not a.IsDynamic and not a.EntryPoint:
                if config.standalone:
                    if n.Name.StartsWith("IronPython") or \
                        n.Name in ['Microsoft.Dynamic', 'Microsoft.Scripting']:
                        embedDict[n] = a
                
                # hdunn 3/15/2018 any(n.Name in dlln for dlln in dllNames) or \ above
                if any(n.Name in dlln for dlln in dllNames):
                    embedDict[n] = a
                if config.libembed and 'StdLib' in n.Name:
                    embedDict[n] = a
                    
        for name, assem in embedDict.iteritems():
            print "\tEmbedding %s %s" % (name.Name, str(name.Version))
            print '\t path ' + str(assem.Location) 
            if assem.Location:
                print 'exist' + str(System.IO.File.Exists(assem.Location))
                if System.IO.File.Exists(assem.Location):
                    f = System.IO.FileStream(assem.Location, System.IO.FileMode.Open, System.IO.FileAccess.Read)
                    mb.DefineManifestResource("Dll." + name.Name, f, ResourceAttributes.Public)
                
        # we currently do no error checking on what is passed in to the AssemblyResolve event handler
        assemblyResolveMethod = tb.DefineMethod("AssemblyResolve", MethodAttributes.Public | MethodAttributes.Static, clr.GetClrType(Assembly), (clr.GetClrType(System.Object), clr.GetClrType(System.ResolveEventArgs)))
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
        staticConstructor = tb.DefineConstructor(MethodAttributes.Public | MethodAttributes.Static, CallingConventions.Standard, System.Type.EmptyTypes)
        gen = staticConstructor.GetILGenerator()
        gen.EmitCall(OpCodes.Call, clr.GetClrType(System.AppDomain).GetMethod("get_CurrentDomain"), ())
        gen.Emit(OpCodes.Ldnull)
        gen.Emit(OpCodes.Ldftn, assemblyResolveMethod)
        gen.Emit(OpCodes.Newobj, clr.GetClrType(System.ResolveEventHandler).GetConstructor((clr.GetClrType(System.Object), clr.GetClrType(System.IntPtr))))
        gen.EmitCall(OpCodes.Callvirt, clr.GetClrType(System.AppDomain).GetMethod("add_AssemblyResolve"), ())
        gen.Emit(OpCodes.Ret)

    mainMethod = tb.DefineMethod("Main", MethodAttributes.Public | MethodAttributes.Static, int, ())
    if config.target == System.Reflection.Emit.PEFileKinds.WindowApplication and config.mta:
        mainMethod.SetCustomAttribute(clr.GetClrType(System.MTAThreadAttribute).GetConstructor(()), System.Array[System.Byte](()))
    elif config.target == System.Reflection.Emit.PEFileKinds.WindowApplication:
        mainMethod.SetCustomAttribute(clr.GetClrType(System.STAThreadAttribute).GetConstructor(()), System.Array[System.Byte](()))

    gen = mainMethod.GetILGenerator()

    # get the ScriptCode assembly...
    if config.embed:

        # put the generated DLL into the resources for the stub exe
        w = mb.DefineResource("IPDll.resources", "Embedded IronPython Generated DLL")
        # print 'IPDLL NAME: ' + 'IPDLL.' + config.output
        # 4/4/2018 Copyright 2018 - hdunn. Apache 2.0 licensed. Modified from original.----- IPDLL NAME
        strPathRefIPDll = System.IO.DirectoryInfo(config.output).Name
        #---  'Changed to: ' + "IPDll." + strPathRefIPDll
        # comment out System.IO.File.Exists(config.output + ".dll"))
        # w.AddResource("IPDll." + config.output, System.IO.File.ReadAllBytes(config.output + ".IPDLL"))
        w.AddResource("IPDll." + strPathRefIPDll, System.IO.File.ReadAllBytes(config.output + ".IPDLL"))
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
    tb.CreateType()
    ab.SetEntryPoint(mainMethod, config.target)
    ab.Save(aName.Name + ".exe", config.platform, config.machine)
    if config.verbose: print 'Gen emit ... done'
    if config.verbose: print "Save as " +  aName.Name + ".exe"
    System.IO.File.Delete(config.output + ".IPDLL")
        
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
        if 'StdLib' not in config.output:
            print 'Compiling with config:\n'
            res = "Input Files - see:{}\n".format(config.output + '.txt')
            
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
        
    if config.verbose: print "Setting up full compile: "
    
    #hdunn 4/3/2018 -try clr.CompileMods
    msg = ''
    if config.verbose: 
        msg = '\nSending internal to clr.ComplierModules:\n'
        msg = msg + '\tconifg.ouput is: {}\n'.format(config.output)
        msg = msg + '\tconfig.main_name is: {}\n'.format(config.main_name)
    
    if config.files and config.verbose: 
        #hdunn 4/6/2018 output ----------
        if 'StdLib' in config.output:
            cfiles = list(config.files)
            cfiles.sort()
            with open( config.output + '.txt', 'w') as tw:
                tw.writelines(('\n').join(cfiles))
        else:            
            msg = msg + ('\tconfig.files:\n\t' + '{} \n\t'*len(config.files)) \
                            .format(*config.files)      
        
            print 'config.files len: ' + str(len(config.files))
            print 'config.files type: ' + str(type(config.files))
                            
    elif config.verbose:
        msg = msg + '\nconfig.files is empty:'    
        
    print str(msg)
    #hdunn 4/6/2018 Try ----------
    try:
        print 'Compiling dlls ...'
       
        clr.CompileModules(config.output + ".dll", 
                           mainModule = config.main_name,
                           *config.files)
        
    except Exception as ex:
        msg = 'FATAL ERROR - Internal clr.ComplierModules:\n'
        msg = msg + '\tconifg.ouput is {}\n'.format(config.output)
        msg = msg + '\tconfig.main_name is {}\n'.format(config.main_name)
        print 'msg create'
        if config.files:
            msg = msg + ('\tconfig.files:\n\t' + '{} \n\t'*len(config.files)) \
                        .format(*config.files)
        else:
            msg = msg + '\tconfig.files is empty'
        
        print(str(ex)[:255] + ' ...' + '\n' + msg)
    
    if config.target != System.Reflection.Emit.PEFileKinds.Dll:
        # read bytes while using dll in compile
        # 4.11.2018 Copyright 2018 - hdunn. Apache 2.0 licensed. Modified from original.
        System.IO.File.Copy(config.output + ".dll", 
                            config.output + ".IPDLL",
                            True)
        # ------------------------------------------
        #config.dlls.append(config.output + '.dll')
        if config.verbose: print 'Gen Start'
        GenerateExe(config)
        
     #hdunn 3/19/2018 commented out ------------
    #    ext = Ext(config.target)
    #    print "Saved to %s" % (config.output + ext, )

if __name__ == "__main__":
    try:
        Main(sys.argv[1:])
    except Exception as ex:
        print(ex)
