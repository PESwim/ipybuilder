# -*- coding: utf-8 -*-
"""
.. created on Thu Jan 18 23:55:19 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

:method: makeBuild() internal call

Compile the exe or dll files given the user information

Use modified pyc.py to compile with subprocess call to
IronPython ipy.exe.

Stop build on partialError that is Fatal to Compile
Let makeBuild finish so that user can fix partialErrs

Assembly setup:

Embedding or standalone changes the path to imports:
  Use AddRef in the .py compiled module to access embedded
  libs used. AddRef IronPython is not required. After AddRef
  you need to import.

  Lists of dlls are compiled into one <App>DLL file. <App> is the
  name of the main .py file.  See Examples.

+-----------+-------+-----------------+-------------------------------+
| flag (exe)| state | parameter(s)    | ipy run result                |
+===========+=======+=================+===============================+
|standalone |       | listexe         | Self embedded: AddRef <App>DLL|
|           |       |                 | Distribute & AddRef Stdlib    |
|           |       |                 | if Lib imports (i.e. zip, etc)|
|           |       |                 | Can run without Ironpython.   |
|plus embed | true  +-----------------+-------------------------------+
|           |       | listdll         | User libs embedded: AddRef    |
|           |       |                 | <App>DLL.dll, imports in .py  |
|           |       |                 | Can run without Ironpython.   |
+-----------+-------+-----------------+-------------------------------+
|standalone |       | any or None     |                               |
|           |       |                 |                               |
|plus embed | true  |                 | AddRef - <App>DLL if lists    |
|           |       |                 |                               |
|plus       |       |                 | AddRef - StdLib as requir'd   |
|libembed   |       | listexe/listdll | Can run without Ironpython.   |
+-----------+-------+-----------------+-------------------------------+
|           |       |                 | Distribute and AddRef Stdlib  |
|standalone | true  | all any or Non  | if Lib imports (i.e. zip, etc)|
|           |       |                 | Can run without Ironpython.   |
+-----------+-------+-----------------+-------------------------------+
|           |       | listexe and/or  | modules.py (listexe) and .dlls|
|   embed   | true  | listdll         | (listdll) embedded. AddRef -  |
|           |       |                 | <App>DLL and StdLib if reqr'd |
|           |       |                 | Imports within app.exe        |
+-----------+-------+-----------------+-------------------------------+
|           |       |                 | Import modules.py and .dlls   |
|   all     | false | listexe and     | (listdll) copied to outdir.   |
|           |       | listdll         | Distribute with app.exe.      |
+-----------+-------+                 +-------------------------------+
| libembed  | true  |                 | Distribute and AddRef Stdlib  |
+-----------+-------+-----------------+-------------------------------+

+-----------+-------+-----------------+-------------------------------+
| flag (dll)| state | parameter(s)    | ipy run result                |
+===========+=======+=================+===============================+
|           |       | listexe         | <App>DLL, .py modules needed  |
| no effect |       |                 | in path. AddRef <App>DLL      |
|           |  NA   +-----------------+-------------------------------+
|           |       | listdll         | User libs need to AddRef      |
|           |       |                 |                               |
+-----------+-------+-----------------+-------------------------------+

"""
clr = None
try:
    import clr
    clr.AddReference("System")
    import System
except Exception:
    pass

from version import __version__
import sys
import os
from os import path as op
from os.path import abspath as opabs
from os.path import exists as opex
from os.path import join as opj
from os.path import normpath as opn
from os.path import dirname as opd
from os.path import basename as opb
from os.path import relpath as oprel
import json
import glob
import subprocess
from subprocess import PIPE
from makedefault import ndcDict
from buildlogs import dynfile
from partialerror import partialError
from globalstate import gsBuild

log = dynfile(__name__)
log.debug('\n---------------- ' + str(__name__) + \
              ' loaded --------------------')
sys.path.append('..\ironpython')

class CompileVars(object):
    '''
       Consolidate all system and user input values for compile run.

    '''

    def __init__(self):
        pass

compiler = CompileVars()

def makeBuild(config):
    '''
       Compile the exe or dll files based on:
         - user args
         - user assembly flags (f_embed, f_libembed, f_standalone)

    '''
    gsBuild.OK = True
    _setCompilerClass(config)
    if gsBuild.Verbose:
        log.info('\n compiler {}'.format(json.dumps(compiler,
                                          default=lambda x: x.__dict__,
                                          indent=4)))
    _fetchLib()

    if compiler.f_parerr:
        return False

    gbm = []
    dllNames = []
    if compiler.lstdll:
        dllNames = list(createUserLibs(config))
        
    # std stub useless unless just an exe way to run a few single python modules
    if  compiler.ext.replace('.', '') == 'exe':
        gbm = gbm + _setupBaseExe(config, dllNames)
        if gsBuild.Verbose: gbm = gbm + ['-v'] # pass verbose to pyc
        
        ipystr = [compiler.ipath + '/ipy '] + [compiler.pycpath] + gbm
        _subprocPYC(ipystr, compiler.mainfile, dotExt='.exe')

        # ADD, SO DELETED
        if compiler.f_embed or compiler.f_standalone:
            dllNames.append(compiler.mainoutdir + '.dll')
        
        # THIS IS OK
        if os.path.isfile(compiler.mainoutdir + '.IPDLL'):
#            log.error('\n trying to remove {}'.format(compiler.mainoutdir + '.IPDLL'))
            try:
                os.remove(compiler.mainoutdir + '.IPDLL')
            except (IOError, Exception) as ex:
                log.error('\n Failed to del/remove:\n {}'.format(compiler.mainoutdir + '.IPDLL'))
                if ex == IOError:
                    print(ex)#pass
                elif ex == System.IO.IOException:
                    print(ex)#pass
                elif ex == WindowsError:
                    print 'Type Err: {}'.format(type(ex))
                    print(ex)#pass
                else:
                    print 'Type Err: {}'.format(type(ex))
                    print(ex)
                    #raise ex
                    
        #TODO checkjust use compiler.f_libembed            
        if (compiler.f_embed or compiler.f_standalone) and compiler.f_libembed:
            if os.path.isfile(opd(compiler.mainoutdir) + 'StdLib.dll'):
                try:
                    os.remove(opd(compiler.mainoutdir) + 'StdLib.dll')
                except IOError as ex:
                    pass
        if gsBuild.Verbose or not gsBuild.INFO:
            pycInfo()

        #pyc does not send .exe to mainoutdir
        if 'dll' not in compiler.ext:
            movestr = ['cmd', '/C', 'move', compiler.pycdir,
               opn(opd(compiler.mainoutdir) + '\\')]

            _subprocMove(movestr, compiler.pycdir,
                         compiler.mainoutdir, compiler.ext)

            if compiler.f_embed or compiler.f_standalone:
                notDelDll = []
                for dll in dllNames:
                    if os.path.isfile(dll) and dll.find('.dll') != -1 and \
                        dll.find('IronPython') == -1: #some ver deleted probably not needed
#                        log.error('\n trying to remove {}'.format(dll))
                        try:
                            os.remove(dll)
#                            log.error('\n successfully removed {}'.format(dll))
                        except (IOError, Exception) as ex:
                            if ex == IOError:
                                print(ex)#pass
                            elif ex == System.IO.IOException:
                                print(ex)#pass
                            elif ex == WindowsError:
                                print 'Type Err: {}'.format(type(ex))
                                print(ex)#pass
                            else:
                                print 'Type Err: {}'.format(type(ex))
                                print(ex)
                            #raise ex
                            notDelDll.append(dll)

                if notDelDll:
                    gsBuild.DELDLLS = notDelDll
                    
    elif compiler.ext.replace('.', '') == 'dll':
        gbm = []
        gbm = gbm + _setupBaseDll(config, dllNames)
        if gsBuild.Verbose: gbm = gbm + ['-v'] # pass verbose to pyc

        ipystr = [compiler.ipath + '/ipy '] + [compiler.pycpath] + gbm
        _subprocPYC(ipystr, compiler.mainfile)

def pycInfo():
    log.info('\n standalone: {}\n embed: {}\n libembed: {}'\
             .format(compiler.f_standalone, compiler.f_embed, 
                     compiler.f_libembed))
    
    if compiler.f_standalone:
        if not compiler.f_embed:
            if not compiler.f_libembed:

                log.info(
                '\n\n Compiling Standalone exe - will run if Windows .net' + \
                '\n framework 4.0+ installed for python built-ins:' + \
                '\n StdLib "AddRef" with distributed StdLib.dll for imports.' + \
                '\n Python or IronPython Libaries for imports must be path' + \
                '\n loadable if StdLib is not part of distribution' + \
                '\n Your project .dll, any relative filepath directory' + \
                '\n strucutres must accompany any distribution (i.e. unzip - zipped dirs).\n')

            elif compiler.f_libembed:

                log.info(
                '\n\n Compiling Standalone exe - with embeded StdLib.dll.' + \
                '\n the StdLib.dll embedded file size is ~ 22 mb. Applicaiton' + \
                '\n exe will run if Windows .net framework 4.0+ installed.' + \
                '\n Python built-ins: no separate distributions required.' + \
                '\n Any relative filepath directory strucutres must' + \
                '\n accompany any distribution (i.e. unzip - zipped dirs).\n')

        elif compiler.f_embed:

            if not compiler.f_libembed:

                log.info(
                '\n\n Compiling Standalone exe - will run if Windows .net' + \
                '\n framework 4.0+ installed for python built-ins:' + \
                '\n StdLib "AddRef" with distributed StdLib.dll for imports.' + \
                '\n Python or IronPython Libaries for imports must be path' + \
                '\n loadable if StdLib is not part of distribution' + \
                '\n any relative filepath directory strucutres must' + \
                '\n accompany any distribution (i.e. unzip - zipped dirs).\n')

            elif compiler.f_libembed:

                log.info(
                '\n\n Compiling Standalone exe - with embeded StdLib.dll.' + \
                '\n the StdLib.dll embedded file size is ~ 22 mb. Applicaiton' + \
                '\n exe will run if Windows .net framework 4.0+ installed.' + \
                '\n Python built-ins: no separate distributions required.' + \
                '\n Any relative filepath directory strucutres must' + \
                '\n accompany any distribution (i.e. unzip - zipped dirs).\n')

    elif compiler.f_embed and not compiler.f_libembed:

        log.info(
        '\n\n Compiling Application embedded dlls into exe stub' + \
        '\n relative python modules or StdLib "AddRef" for imports.' + \
        '\n Python or IronPython Libaries for imports must be path' + \
        '\n loadable if StdLib is not part of distribution' + \
        '\n Limited use case for "exe": Must have IronPython installed and ' + \
        '\n any relative filepath directory strucutres must accompany any' + \
        '\n distribution (i.e. unzip - zipped dirs).\n')


    elif compiler.f_embed and compiler.f_libembed:

        log.info(
        '\n\nCompiling exe - with embeded StdLib.dll: Limited use case.' + \
        '\n The StdLib.dll embedded file size is ~ 22 mb. Applicaiton' + \
        '\n exe will run if Windows .net framework 4.0+ and IronPyhton' + \
        '\n installed. IronPython built-ins are now embedd, but without' + \
        '\n using the "/standalone" = true optione you still need to' + \
        '\n distribute required IronPython executables and Dll files.' + \
        '\n Any relative filepath directory strucutres must' + \
        '\n accompany any distribution (i.e. unzip - zipped dirs).\n')

    else:
        log.info('\n\nCompiling Application dlls and exe stub' + \
              '\n - relative python modules for imports' + \
              '\n - limited use case "exe": must have IronPython installed' + \
              '\n and dll must accompany any distribution.\n')


def createUserLibs(config):
    '''
       Loads files from user arg "listdll".
       If .py file creates .dll then/else adds
       created or listdll .dll file to to compiler config.dlls.

       If assembly f_embed or f_standalone:
           is true:
             Agglomerates all dll libraries into one dll
             that is embeded and then removed from
             user arg "outDir" or or auto-named outdir.
           else:
               Add each lib .dll file to "outDir" or outdir.

    '''

    dllNames = []
    if not compiler.lstdll:
        return []

    dllName = None
    gb = []

    if isinstance(compiler.lstdll, list):
        for resfile in compiler.lstdll:
            if '.py' not in resfile:
                #skip compile
                if '.dll' in resfile:
                    dllNames.append(resfile)
                continue

            if resfile and '.py' in resfile:
                dllName = opj(opd(compiler.mainoutdir),
                              opb(resfile).replace('.py', ''))

                dllNames.append(dllName + '.dll')

                gb.append(resfile)

            if not compiler.f_embed and not compiler.f_standalone:

                gb.extend(_getAssembly(config))
                gb.append("/out:" + dllName)
                gb.append("/target:dll")
                gb = nullList(gb)
                
                ipystr = [compiler.ipath + '/ipy'] + [compiler.pycpath] + gb
                _subprocPYC(ipystr, dllName, '.dll')
                gb = []
                continue
        
        # make one lib dll to embed
        if compiler.f_embed or compiler.f_standalone:
            
            dllNames = []
            gb.extend(_getAssembly(config))
            
            dllName = opj(opd(compiler.mainoutdir),
                          ('.').join(compiler.mainout.split('.')[:-1]) +'DLL')
            
            dllNames.append(dllName + '.dll')
            
            gb.append("/out:" + dllName)
            gb.append("/target:dll")
            gb = nullList(gb)

            ipystr = [compiler.ipath + '/ipy'] + [compiler.pycpath] + gb
            _subprocPYC(ipystr, dllName, '.dll')
                   
        return dllNames
    return None

def nullList(gbm):

    if isinstance(gbm, list):
        gbm = list(gbm)
        nullList = list(gbm)
        for i, arg in enumerate(nullList):
            if not arg or arg == None:
                del gbm[i]
        if gbm:
            return gbm
    elif gbm and gbm != None:
        return gbm

    return None

def _createStdLib():

    if gsBuild.Verbose or not gsBuild.INFO:
        log.info('\nNew StdLib compile: {}'.format(compiler.stdlibsource))

    gb0 = glob.glob(opn(opj(compiler.libpath, '*.py')))
    gb1 = glob.glob(opn(opj(compiler.libpath, '\*.py')))
    gb2 = glob.glob(opn(opj(compiler.libpath, '*\*.py')))
    gb3 = glob.glob(opn(opj(compiler.libpath, '*\*\*.py')))

    gb = list(gb0 + gb1 + gb2 + gb3)

    gb.append("/out:" + compiler.stdlibsource.replace('.dll', ''))
    gb.append("/target:dll")

    ipystr = [compiler.ipath + '/ipy'] + [compiler.pycpath] + gb
    if _subprocPYC(ipystr, opabs(compiler.stdlibsource), dotExt=None):
        if op.isfile(opabs(compiler.stdlibsource)):
            log.FILE('Build Created: {}' \
                     .format(opabs(compiler.stdlibsource)))

    compiler.isStdLib = op.isfile(opabs(compiler.stdlibsource))

def _fetchLib():
    if gsBuild.IPATH != 'clr':
        assert compiler.isStdLib, \
            'need a Stdlib file in:\n {}'.format(compiler.stdlibsource)

    if not compiler.f_libembed and not compiler.isReleasedStdLib:
        if compiler.stdlibsource:
            copystr = ['cmd', '/C', 'copy', compiler.stdlibsource, \
                       opd(compiler.stdlibrelease)]

            if _subprocCopy(copystr,compiler.stdlibsource):
                log.FILE('Copied {}'.format(compiler.stdlibrelease))

    if not compiler.haveStdLib and compiler.stdlibsource:
        copystr = ['cmd', '/C', 'copy', compiler.stdlibsource, os.getcwd()]

        if _subprocCopy(copystr,compiler.stdlibsource):
            log.FILE('Copied {}'.format(opj(os.getcwd(), 'StdLib.dll')))

    libsaved = []
    
    if compiler.stdlibsource and op.isfile(compiler.stdlibsource):
        libsaved.append(compiler.stdlibsource)
    if compiler.stdlibrelease and op.isfile(compiler.stdlibrelease):
        libsaved.append(compiler.stdlibrelease)
    if op.isfile(opj(os.getcwd(), 'StdLib.dll')):
        libsaved.append(opj(os.getcwd(), 'StdLib.dll'))
    
    if gsBuild.Verbose and libsaved:
        log.info(('\nStdLib exists/saved in:\n' + '{}\n'*len(libsaved)) \
                 .format(*libsaved))
        return
    
    elif libsaved:
        return
    
    elif clr:
        log.error("\nCouldn't create StdLib - Continuing, will try " + \
                  "\ninternal lib: exe fail = Need ironpython 2.7 distribution")
        return
    
    raise NotImplementedError('Need ironpython 2.7 distribution ' + \
                              'in something like ../ironpython path')

def _getAssembly(config):

    assemInfo = config['ASSEMBLY']
    gbm = []
    if assemInfo['company'] and assemInfo['company'] != '':
        gbm.append('/file_info_company:'+ assemInfo['company'])
    if assemInfo['product_version'] and assemInfo['product_version'] != '':
        gbm.append('/file_info_product_version:'+ assemInfo['product_version'])
    if assemInfo['product_name']and assemInfo['product_name'] != '':
        gbm.append('/file_info_product:'+ assemInfo['product_name'])
    if assemInfo['copyright'] and assemInfo['copyright'] != '':
        gbm.append('/file_info_copyright:'+ assemInfo['copyright'])
    if assemInfo['file_version'] and assemInfo['file_version'] != '':
        gbm.append('/file_version:'+ assemInfo['file_version'])

    #    #TODO Next Version 0.0.11.20
    #    if assemInfo['platform'] and assemInfo['platform'] != "":
    #        gbm.append('/platform:'+ assemInfo['platform'])
    #    
    #    if assemInfo['target'] and (assemInfo['target'] == 'false' or \
    #        assemInfo['target'] == '' or assemInfo['target'] == 'None'):
    #        gbm.append('/target:'+ 'dll')    
    #    elif assemInfo['target'] and (assemInfo['target'] == 'true' or \
    #        assemInfo['target'] == 'exe'):
    #        gbm.append('/target:'+ 'exe')    
    #    elif assemInfo['target'] and (assemInfo['target'] == 'win' or \
    #        assemInfo['target'] == 'winexe'):
    #        gbm.append('/target:'+ 'winexe')
        
    gbm = nullList(gbm)
    return gbm

def _setCompilerClass(rconfig):
    clr = None
    try:
        import clr
    except Exception as ex:
        pass
    
    config = ndcDict(rconfig)
    f_standalone = None
    f_embed = None
    f_libembed = None
    f_parerr = None
    # f_parerr - Stop build on partialError that is Fatal to Compile
    # Let makeBuild finish so that user can fix partialErrs

    with open(config['CONFIGPATH'], 'r') as jbcr:
        config = ndcDict(json.load(jbcr))

    if gsBuild.Verbose or not gsBuild.INFO:
        log.info('\n Building from CONFIG:\n {}\n'.format(json.dumps(config,indent=4)))

    if not opex(config['MAINFILE']):
        try:
            raise IOError
        except IOError as ex:
            msg = 'File Filepath does Not exist:\n "{}"' \
                    .format(config['MAINFILE'])
            partialError(ex, msg)
            f_parerr = True

    if not f_parerr:
        log.FILE('Build Loaded: {}'.format(config['MAINFILE']))

    assemInfo = config['ASSEMBLY']
    if isinstance(assemInfo['standalone'], bool) or \
        str(assemInfo['standalone']).upper() in ['TRUE', 'FALSE']:
        f_standalone = True if str(assemInfo['standalone']).upper() == \
                                                            'TRUE' else False
    if isinstance(assemInfo['embed'], bool) or \
        str(assemInfo['embed']).upper() in ['TRUE', 'FALSE']:
        f_embed = True if str(assemInfo['embed']).upper() == 'TRUE' else False

    if isinstance(assemInfo['libembed'], bool) or \
        str(assemInfo['libembed']).upper() in ['TRUE', 'FALSE']:
        f_libembed = True if str(assemInfo['libembed']).upper() \
                        == 'TRUE' else False

    ext = '.dll'
    if config['MAKEEXE'] == True or \
        str(config['MAKEEXE']).upper() == 'TRUE':
        ext = '.exe'

    if f_standalone and not config['MAKEEXE']:
        log.warn('\n** Switching to exe /stanalone == true in Assembly:' + \
                 '\n {}\n   Overrides default or makeEXE input arg == False' \
                 .format(config['JSONPATH']))
    
    STDLIBSOURCE = None
    LIBPATH = None
    MAINOUT = opn(opj(config['OUTDIR'], ('.').join(opb(config['MAINFILE']) \
                      .split('.')[:-1])) + ext)

    CLRALTLIBPATH = opn(opj(opd(opabs(gsBuild.IPYBLDPATH)), 'StdLib.dll'))

    if gsBuild.Verbose: log.info('\nIPATH {}'.format(gsBuild.IPATH))
    IPATH = gsBuild.IPATH
    
    if IPATH == 'clr':
        LIBPATH = '/lib'
        if opex(CLRALTLIBPATH):
            STDLIBSOURCE = CLRALTLIBPATH
    else:
        if opex(opabs(opj(IPATH, 'StdLib.dll'))):
            STDLIBSOURCE = opabs(opj(IPATH, 'StdLib.dll'))
        else:
            STDLIBSOURCE = 'StdLib.dll' 
        LIBPATH = opabs(opj(IPATH, 'Lib'))
    
    if gsBuild.Verbose:
        log.info('\n gsBuild.IPYBLDPATH {}'.format(gsBuild.IPYBLDPATH))
    
    compiler.pycpath = (opn(opd(opabs(gsBuild.IPYBLDPATH)))) + '\pyc.py'
    compiler.stdlibsource = STDLIBSOURCE
    compiler.ipath = IPATH
    compiler.libpath = LIBPATH
    
    if STDLIBSOURCE and not op.isfile(STDLIBSOURCE) and IPATH != 'clr':
        _createStdLib()
    
    elif STDLIBSOURCE and not op.isfile(STDLIBSOURCE) and IPATH == 'clr':
        if gsBuild.Verbose or not gsBuild.INFO:
            log.info('\n Cannot create StdLib without Ironpython installed.' + \
                     'Trying compile with internal StdLib Ref.')
    
    MAINOUTDIR = ('.').join(MAINOUT.split('.')[:-1])
    PYCDIR = opn(opj(os.getcwd(), opb(MAINOUTDIR)) + ext)
    STDLIBRELEASE = opj(opd(MAINOUTDIR), 'StdLib.dll')
    MAINFILE = config['MAINFILE']
    isLib = opex(LIBPATH)
    isStdLib = False
    if STDLIBSOURCE:
        isStdLib = op.isfile(STDLIBSOURCE)
    haveStdLib = op.isfile(opj(os.getcwd(), 'StdLib.dll'))
    isReleasedStdLib = False
    if STDLIBRELEASE:
        isReleasedStdLib = op.isfile(STDLIBRELEASE)

    lstdll = []
    if config['LISTFILES']['dll']:
        if isinstance(config['LISTFILES']['dll'], list):
            for lfile in config['LISTFILES']['dll']:
                if lfile and '__init__' not in lfile:
                    lstdll.append(lfile)
        else:
            lstdll.append(config['LISTFILES']['dll'])

    lstexe = []
    if config['LISTFILES']['exe']:
        if isinstance(config['LISTFILES']['exe'], list):
            for xfile in config['LISTFILES']['exe']:
                if xfile and '__init__' not in xfile:
                    lstexe.append(xfile)
        else:
            lstexe.append(config['LISTFILES']['exe'])

        lstexe = nullList(lstexe)

    compiler.f_standalone = f_standalone
    compiler.f_embed = f_embed
    compiler.f_libembed = f_libembed
    compiler.f_parerr = f_parerr
    compiler.mainout = MAINOUT
    compiler.ipath = IPATH
    compiler.mainoutdir = MAINOUTDIR
    compiler.pycdir = PYCDIR
    compiler.stdlibrelease = STDLIBRELEASE
    compiler.stdlibsource = STDLIBSOURCE
    compiler.libpath = LIBPATH
    compiler.mainfile = MAINFILE
    compiler.isLib= isLib
    compiler.isStdLib = isStdLib
    compiler.haveStdLib = haveStdLib
    compiler.isReleasedStdLib = isReleasedStdLib
    compiler.lstdll = lstdll
    compiler.lstexe = lstexe
    compiler.ext = ext
    compiler.lstexedlls = None
    
    if not opex(opd(compiler.pycdir)):
        raise IOError('FilePath {}:\t Use absolute or relative to:\n\t {}' \
                      .format(opd(compiler.pycdir), os.getcwd()))
    if compiler.f_standalone:
        if gsBuild.Verbose or not gsBuild.INFO:
            log.info('\nNew {} compile standalone from:\n {}' \
                            .format(ext.upper().replace('.', ''),
                                    config['MAINFILE']))
    else:
        mfn = 'application/lib'
        if config['MAINFILE']:
            mfn = opb(config['MAINFILE'])
        if gsBuild.Verbose or not gsBuild.INFO:
            log.info(("\nNew {} compile from: \n {}" + \
                      "\n\tAs Required: add your {}, project, and ironpython"+ \
                      "\n\tdll(s) to path:\n\t{}\n\n")
                     .format(ext.upper().replace('.', ''),
                             config['MAINFILE'], mfn,
                             config['OUTDIR']))

    if gsBuild.Verbose or not gsBuild.INFO:
        log.info('\n Lib source path {}'.format(LIBPATH))
        log.info('\n "IF" set "True", f_libembed adds ~23mb to file:' + \
                 'now set as {}'.format(compiler.f_libembed))

    if compiler.f_libembed and compiler.isStdLib:
        if gsBuild.Verbose or not gsBuild.INFO:
            if compiler.isReleasedStdLib:
                log.info('\nOK - "StdLib.dll" exists delete'+ \
                         ' or move to update:\n{}'.format(STDLIBRELEASE))
            else:
                log.info('\nOK - "StdLib.dll" exists delete'+ \
                         ' or move to update:\n{}'.format(STDLIBSOURCE))

    elif not compiler.isStdLib and compiler.f_libembed and \
        not compiler.isReleasedStdLib and compiler.isLib:

        _createStdLib()
#    log.error('\n clr refs {}' \
#              .format(str(clr.References).split(',')))    
#    log.error('\n stdlib test {}' \
#              .format(any('StdLib' in clref \
#                              for clref in str(clr.References).split(','))))
    f_haveclrStdLib = None
    if clr:
        f_haveclrStdLib = any('StdLib' in clref \
                                  for clref in str(clr.References).split(','))
    
    if (not clr and not compiler.isStdLib) or (clr and not f_haveclrStdLib):
        raise NotImplementedError('StdLib: Need IronPython2.7 distribution' + \
                                  ' in something like ../ironpython path')
    
def _setupBaseExe(config, dllNames):
    gbm = []
    gbm.append("/main:" + compiler.mainfile)

    if isinstance(compiler.lstexe, list):
        for resfile in compiler.lstexe:
            if '.py' in resfile:
                gbm.append(resfile)

    if dllNames:
        for dll in dllNames:
            gbm.append(dll)

    if compiler.f_embed:
        gbm.append("/embed")

    if compiler.f_standalone:
        gbm.append("/standalone")

    if compiler.f_libembed:
        gbm.append("/libembed")
        
    gbmx = []
    gbmx = _getAssembly(config)
    if gbmx:
        gbm.extend(gbmx)
    gbm.append("/out:" + compiler.mainoutdir)
    gbm.append("/target:exe")
    
    return list(gbm)

def _setupBaseDll(config, dllNames):

    gbm = []
    gbm.append("/main:" + compiler.mainfile)

    if isinstance(compiler.lstexe, list):
        for resfile in compiler.lstexe:
            if '.py' in resfile:
                gbm.append(resfile)

    if dllNames:
        for dll in dllNames:
            gbm.append(dll)

    gbm.append("/out:" + compiler.mainoutdir)
    gbm.append("/target:dll")

    return list(gbm)

def _subprocCopy(copyCmd, source):

    try:
        subprocess.check_output(copyCmd)
    except subprocess.CalledProcessError:
        msg = 'StdLib  File | Filepath:\n{} ' \
              '\n\t- access denied or does not exist'.format(source)
        raise IOError(msg)
    return True

def _subprocMove(moveCmd, source, dest, dotExt):
    
    po = None
    rpath = dest
 
    if dotExt:
        rpath = rpath + dotExt
    
    clr = None # keep out global clr
    try:
        import clr    
    except Exception as ex:
        pass
    
    if clr:
        try:
            clr.AddReference("System")
            import System
        except Exception as ex:
            pass

        if System.IO.File.Exists(rpath):
            if System.IO.File.Exists(rpath):
                System.IO.File.Delete(rpath)
        if System.IO.File.Exists(source):
            try:
#                log.error('\n Try noving:\n\t{}\n To:\n\t\n\t{}' \
#                          .format(source,rpath))
                System.IO.File.Move(source,rpath)
                
            except Exception as ex:
                print('Failed to Move:\n\t{}'.format(source))
                print(ex)
                
    elif not clr and os.path.isfile(rpath):
        try:
            os.remove(rpath)
        except IOError as ex:
            pass
        if os.path.isfile(source):
            
            try:
#                log.error('\n Try noving:\n\t{}\nTo:\n\t\n{}' \
#                              .format(source,dest))
                po = subprocess.check_output(moveCmd)
            except subprocess.CalledProcessError as ex:
                try:
                    msg = str(ex)
                    raise IOError(msg)
                except IOError as exc:
                    msg = 'Move failed File | Filepath \n{} ' \
                          '- access denied or does not exist:\n\t{}' \
                          .format(source, ex.message)
                    partialError(exc, msg)

    if po and 'moved' not in str(po):
        log.info('\nRelative path resolution Error:\n {} \nmoving to {}' \
                 .format(source,
                         rpath))

    elif (clr or po) and op.isfile(rpath):
        if gsBuild.Verbose: log.info('Build Moved: {}'.format(rpath))
        
        log.FILE('Build Moved: {}'.format(rpath))

def _subprocPYC(strCmd, cmpfile, dotExt='.dll'):

    clr = None # keep out global clr
    try:
        import clr    
    except Exception as ex:
        pass
    
    if clr:
        try:
            sys.path.append(oprel(compiler.pycpath))
            import pyc
        except Exception as ex:
            pass

        try:
            clr.AddReference("StdLib")
        except System.IO.IOException as ex:
            print('StdLib.dll reference error:\n\t' + \
                  'check file | filepath')
        try:
            clr.AddReference("IronPython")
        except System.IO.IOException as ex:
            print('IronPython reference error:\n\t' + \
                  'check file | filepath')
            
        f_ipy = False
        try:
            import ipyver
            rs = ipyver.ReferenceStatus()
            f_ipy = rs.RefStatusIPMS()['ipy']['isLocal']
        except System.IO.IOException as ex:
            pass
        
        try:
            clr.AddReference("ipybuild")
        except System.IO.IOException as ex:
            try:
                clr.AddReference("ipybuilder")
            except System.IO.IOException as ex:
                if f_ipy:
                    print('IF .exe: ipybuild(er) reference error:\n\t' + \
                          'check file | filepath')

        args = None
        rslt = None
        args = strCmd[2:]

        try:
            rslt = pyc.Main(args)
        except Exception as ex:
            errtyp = ''
            gsBuild.OK = False
            try:
                errtyp = ex.GetType().ToString()
            except Exception as exf:
                pass
            if ex:
                log.warn('pyc.Main err:\n' + ex.ToString())
                log.warn('type {} or System Type {}'.format(type(ex), errtyp))
                log.warn('Error: {}'.format(ex))
                print 'ex-err'

            return False
         
        if rslt:
            return True

    else:
        
        po = subprocess.Popen(strCmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = po.communicate()
        po.wait()

        if stderr:
            log.warn('ERR\n {}:\n\t compiling with {}'.format(stderr, cmpfile))
            po.kill()
            gsBuild.OK=False
            return False
     
        else:
            if gsBuild.Verbose or not gsBuild.INFO:
                log.info('\n - STDOUT - \n{}'.format(stdout))

        po.kill()
    
    if dotExt and opex(opj(opd(compiler.mainoutdir), 
                           opb(cmpfile).replace('.py', dotExt))):   
        log.FILE('Build Created: {}'.format(cmpfile.replace('.py', dotExt)))
        return True
    elif opex(cmpfile):
        log.FILE('Build Created: {}'.format(cmpfile))   
        return True
    else:
        gsBuild.OK = False
        return False
