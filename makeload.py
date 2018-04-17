# -*- coding: utf-8 -*-
"""
.. created: on Wed Feb 14 19:39:21 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""

import version
from version import __version__
import sys
import os
op = os.path
opex = os.path.exists
opab = op.abspath
opj = op.join 
opn = op.normpath
opd = op.dirname
opb = op.basename
oprel = op.relpath
import json
import time
import zipfile
import re
from globalstate import gsBuild

import makedefault
from makedefault import defaultconfig, defaultjson, setPath, \
                        ndcDict, defaultcfg

import partialerror
from partialerror import  FatalError, partialError
import buildlogs
from buildlogs import dynfile
log = dynfile(__name__)
log.debug('\n---------------- ' + str(__name__) + \
              ' loaded -----------------')

def AssignPaths(con, main, js, arg_out, uconfig):
    
    PTYPESK = [('json', 'JSONPATH'), ('name', 'MAINFILE'),
               ('config', 'CONFIGPATH'), ('mkdir', 'MAKEDIR'), 
               ('odir', 'OUTDIR')
              ]
    
    uconfig = ndcDict(uconfig)
    # need space to parse not None
    if  not con or con == '' or con == "":
        con = ' '

    for tk in PTYPESK:
        atyp, k = tk
        uconfig[k] = setPath(con, main, js, arg_out, f_type=atyp)

    return ndcDict(uconfig)

def AssignJson(uconfig):

    config = ndcDict(uconfig)

    if config['JSONPATH'] and os.path.isfile(config['JSONPATH']):
        with open(config['JSONPATH'], 'r') as assjr:
            config['ASSEMBLY'] = json.load(assjr)
        log.FILE('Confirmed: {}'.format(config['JSONPATH']))

    elif config['JSONPATH']:
        with open(defaultjson, 'r') as jassr:
            assembly = json.load(jassr)
        log.FILE('Confirmed: {}'.format(defaultjson))

        with open(config['JSONPATH'], 'w') as jassw:
            json.dump(assembly, jassw, indent=4)
        log.FILE('{}'.format(config['JSONPATH']))

        log.info('\n*Use auto-named json on next build:\n "{}"' \
                 .format(config['JSONPATH']))

        log.info(('\nUsing defualt assembly:\n\t {}\n\tSaved as:\n\t {}') \
                 .format(defaultjson, config['JSONPATH']))

        with open(config['JSONPATH'], 'r') as jassr:
            config['ASSEMBLY'] = ndcDict(json.load(jassr))
        log.FILE('Confirmed: {}'.format(config['JSONPATH']))

        log.warn(('\nNo user filepath param - using :\n\t {}') \
                 .format(defaultjson))

    else:
        raise FatalError('SynTaxError', 'Try using fully qualified filepaths')

    return ndcDict(config)

def AssignListFiles(uconfig, args_):

    args = ndcDict(args_)
    config = ndcDict(uconfig)

    if args['listexe']:
        config['LISTFILES']['exe'] = []
        config['LISTFILES']['exe'] = loadRes(args['listexe'])

    if args['listdll']:
        config['LISTFILES']['dll'] = []
        config['LISTFILES']['dll'] = loadRes(args['listdll'])

    for key in config['LISTFILES'].keys():
        if isinstance(config['LISTFILES'][key], list):
            for vfile in config['LISTFILES'][key]:
                if vfile and 'assembly.json' in vfile:
                    vfile = config['JSONPATH']

        elif config['LISTFILES'][key] and \
            'assembly.json' in config['LISTFILES'][key]:
            log.fatal("\nWrong keys in list files: check params")
            config['LISTFILES'][key] = config['JSONPATH']

    return ndcDict(config)

def uniqueZips(zips, zipsExisting):
    
    zipex = list(zipsExisting)
    zips = list(set(zips)) #unique
    addZips = list(zips)
    for zfile in zips: 
        for zex in zipex:
            if zex:
                zf = oprel(zfile).replace('\\','/').replace('../','')
                zx = zex
                if zf == zx:
                    try:                                              
                        addZips.remove(zfile)
                    except ValueError as ex:
                        log.warn('\nUnable to trim duplicate zip additions' + \
                                 '\nzip: {}\narchive {}'.format(zf, zx))
                        msg = '\nUnable to trim duplicate zip additions' + \
                              '\nzip: {}\narchive {}'.format(zf, zx)
                              
                        partialError(ex,msg)          
                        continue
            continue
        
    if addZips and gsBuild.Verbose or not gsBuild.INFO:    
        log.info(('\n addZips:\n' + '{}\n'*len(addZips)).format(*addZips))    
    
    return addZips
            
def AssignMakeZip(uconfig, args):

    config = ndcDict(uconfig)
    outzipPath = None
    cfz = config['ZIPPATH']
    
    if args['listzip']:
        zfiles = [] # missing zipfiles in listzip.txt or input
        zips = loadRes(getTrueFilePath(args['listzip']))
        
        zpl = None
        uzips = None  # unique zips
        if zips:
            zpl = len(zips)
        
        # zip exists with cur name if have zipped before
        isautozip = False
        
        try:
            import zlib
            mode = zipfile.ZIP_DEFLATED
        except ImportError:
            mode = zipfile.ZIP_STORED

        config['LISTFILES']['zip'] = []
        if isinstance(zips, list):
            config['LISTFILES']['zip'].extend(zips)
        else:
            config['LISTFILES']['zip'].append(zips)

        # set outzip path
        manf = 'default.zip'
        if config['MAINFILE']:
            manf = ('.').join(opb(config['MAINFILE']).split('.')[:-1]) + '.zip'
        
        outzipPath = opj(config['OUTDIR'], manf)
        # stop trying to overwrite same file
        # current zip path
        cfzp = None
        if cfz:
            
            try:
                cfzp = getTrueFilePath(cfz)
                if opex(cfzp):
                    isautozip = True 
            except IOError:
                pass
        # auto zip path    
        elif outzipPath:
            try:
                cfzp = getTrueFilePath(outzipPath)
                if opex(cfzp):
                    isautozip = True 
            except IOError:
                pass
        # update zip path
        config['ZIPPATH'] = cfzp
        cfz = cfzp

        # -- zipping ---      
        # uzips      
        if isautozip:
            infoExistZip(cfz, outzipPath)
            log.FILE('Confirmed: {}'.format(cfzp))
            zipsRelative = []
            
            for zipname in zips:
                relname = None
                relname = _getRelativeZipName(zipname)
                if relname:
                    zipsRelative.append(relname)
                else:
                    zipsRelative.append(zipname)
                    
            with zipfile.ZipFile(cfzp, 'a', mode) as ziprd:
                uzips = list(uniqueZips(zipsRelative, list(ziprd.namelist())))
                for zfile in uzips:
                    if not os.path.isfile(zfile):
                        zfiles.append(zfile)
                        continue
                    arcname = _getRelativeZipName(zfile)
                    if not arcname:
                        arcname = oprel(zfile)
                    ziprd.write(zfile, arcname)
                    
            ziprd.close()

            # changed if uzips
            if uzips:
                if gsBuild.Verbose or not gsBuild.INFO:
                    log.info(('\nSome Files already zipped in:\n{}\n\t' + \
                              '- delete to replace existing' + \
                              '\nadding zip files to existing archive:\n' + \
                              '{}\n'*len(uzips)) \
                            .format(cfz, *uzips))
        
        # Need new zip with ZIPPATH/outzipPath as name
        elif not isautozip:   
            warnZip(outzipPath)
            
            if isinstance(zips, list):

                with zipfile.ZipFile(cfz, 'a', mode) as zipr:
                    for zfile in list(set(zips)):
                        if not os.path.isfile(zfile):
                            zfiles.append(zfile)
                            continue
                        
                        arcname = _getRelativeZipName(zfile)
                        if not arcname:
                            arcname = oprel(zfile)
                        zipr.write(zfile, arcname)
                
                log.FILE('{}'.format(config['ZIPPATH']))
                zipr.close()

            if isinstance(zips, (str, unicode)):
                with zipfile.ZipFile(cfz, 'w', mode) as zipr:
                    arcname = oprel(zips)
                    zipr.write(zips, arcname)
                        
                zipr.close()
                log.FILE('{}'.format(cfz))

        if zfiles:
            log.warn(('\nFile | path does not exist - ' +\
                      'skipped adding zip files:\n\t' + \
                       '{} \n\t'*len(zfiles)).format(*zfiles))
    
            log.FILE(('*Missing zip: {}\n'*len(zfiles)).format(*zfiles))
    
            partialError('ValueError',
                        ('*Missing zip: {}\n'*len(zfiles)).format(*zfiles))

    return ndcDict(config)

def _getRelativeZipName(zfile):
    parupCount = 0
    RelDirsFilePath = None

    if '..' in oprel(zfile): 
        parupCount = oprel(zfile).count('..')
    
    if parupCount == 0:
       return 

    zfileDirs = os.path.normpath(zfile).split(os.path.sep)
    useDirs = zfileDirs[-(parupCount+1):]
    RelDirsFilePath = opn(opj((op.sep).join(useDirs)))
    
    if RelDirsFilePath:
        return RelDirsFilePath
    
    return

def AssignArgsConfig(args, uconfig):

    config = ndcDict(uconfig)

    if config['CONFIGPATH'] and os.path.isfile(config['CONFIGPATH']):
        log.FILE('Confirmed: {}'.format(config['CONFIGPATH']))

    if config['MAINFILE']and os.path.isfile(config['MAINFILE']):
        log.FILE('Confirmed: {}'.format(config['MAINFILE']))

    if args['makeEXE']:
        config['MAKEEXE'] = args['makeEXE']

    config = AssignJson(config)
    config = AssignListFiles(config, args)
    config = AssignMakeZip(config, args)

    return ndcDict(config)

def pathRead(fpaths):
    '''
       Try to read a file path or or lst of file paths.

       :params: fpath[s] [str][list] - path[s] to check

       :return: path[s] read [str] or [list]

    '''
    fig = None
    fpaths = _fmtResFiles(fpaths)
    if fpaths and isinstance(fpaths, list):
        fig = []
        for resfile in fpaths:
            filepath = getTrueFilePath(resfile)
            fig.append(filepath)

    elif fpaths and isinstance(fpaths, (str, unicode)):
        fig = getTrueFilePath(fpaths)

    return fig

def warnZip(outzpath):

    log.warn(('\nDirecting zip files to:' +
              '\n\t{}\n\n' +
              '\tZippped resources are auto-named and sent to the\n ' +
              '\tdirectory of the same path as the final main-name.\n') \
              .format(outzpath))

def infoExistZip(cfgz, outzpath):

    cdate = time.strftime('%x %X', time.gmtime(os.path.getmtime(outzpath)))
    if gsBuild.Verbose or not gsBuild.INFO:
        log.info(('\n OK - zip file:\n   "{}" \n resource exists -' + \
                  ' to verify check write logs at time {}') \
                .format(cfgz, cdate))

def CheckConfig(uconfig):
    '''
       Check for valid config entries after parse/loading

       :param: config Dict from LoadConfig [OrderedDict]

       :return:
	       userconfig [config Dict] - as written to file path shown in writefiles.log

       :raise: FatalError or partialError [Exception] or [error sink list]

       *user can re-run ipybuild on a partialError fix*
       *why FatalError - a user messed with defaults - error vs program error*

    '''
    userfig = ndcDict(uconfig)

    if not len([val for val in userfig if val or val != '']) >= 1:
        raise ValueError('need at least one parameter for config')

    if not userfig['MAKEDIR'] or not opex(opd(userfig['MAKEDIR'])):
        raise NameError('bad path to config file {}' \
                        .format(opd(userfig['MAKEDIR'])))

    if not all(k in userfig.keys() for k in defaultconfig.keys()):
        log.error('\n keys {}\n\t{}'.format(str(userfig.keys()), \
                                            str(defaultconfig.keys())))
        raise FatalError('KeyError', 'bad userconfig key set')

    if not userfig['MAINFILE'] or userfig['MAINFILE'] == '':
        raise FatalError('NameError', 'need main name.py')

    if not '.py' in userfig['MAINFILE'] or not opex(userfig['MAINFILE']):
        try:
            raise NameError
        except NameError as ex:
            msg = ' main name "{}" must be .py file and exist' \
            .format(userfig['MAINFILE'])

            partialError(ex, msg)

    if not isinstance(userfig['MAKEEXE'], bool) and \
        str(userfig['MAKEEXE']).upper() not in ['TRUE', 'FALSE']:

        try:
            raise ValueError
        except ValueError as ex:
            msg = 'makeEXE {}: need type bool in params (no key needed)' \
                    .format(userfig['MAKEEXE'])
            partialError(ex, msg)

    if not opex(userfig['JSONPATH']):
        try:
            raise NameError
        except NameError as ex:
            msg = 'bad path to assembly.json file "{}"' \
                        .format(userfig['JSONPATH'])
            partialError(ex, msg)

    if not opex(userfig['CONFIGPATH']):
        try:
            raise NameError
        except NameError as ex:
            msg = 'bad path to assembly.json file "{}"' \
                        .format(userfig['CONFIGPATH'])
            partialError(ex, msg)

def getTrueFilePath(fnpath):
    '''
       Find absolute file path if exists.

       :param: fnpath [str] - file path to check.

       :return: absolute path to existing file [str].

       :raise:  [IOError] if can't find or read.

    '''
    fpath = fnpath.strip()
    resolvedPath = None
    assert isinstance(fpath, (str, unicode)), \
        'Error type not str: send str file path'

    if os.getcwd() not in fpath:
        fpath = opab(fpath)

    dfn = opb(opn(fpath))
    dfdir = opd(opn(opab(fpath)))

    dfpath = None
    dirfs = os.listdir(opd(opn(opab(fpath))))
    dfpath = opn(op.join(dfdir, dfn))
    if dfn in dirfs and op.isfile(dfpath):
#        log.warn('\n  dfpath {}'.format(dfpath))
        resolvedPath = dfpath
        return resolvedPath
    
    elif _validateFileIsPath(dfpath):
        #        log.warn('\n signle filepath return {}'.format(dfpath))
        return dfpath
    
    raise IOError('file | filepath not resolved: {}'.format(fpath))

def LoadConfig(parsedArgs):
    '''
      Load user defined "configPath" or start with auto-renamed 
      default configuration as helper, if started with "two quotes" 
      no space ("") as configPath parameter.
      
	  After user adjustments to default_config.config content or
      name, or path, user will need to re-run using "auto-renamed" 
      config path. 
      
	  The auto-renamed file is *shown as output* in the output log. 
      This will finish a build.

      Provides user opportunity to change defaults in an editor 
      before building on default settings and assembly information.

      If you use "two quotes no space ("") as the first arg then the 
      default config path is used and build proceeds with an 
      auto re-named appname:_config.config file or if no main name was 
      provided the default_config.config file which user can modify. 
      
      If the output path ("ourDir" arg) is not resolved generated files
      go to the "/UserDefaulted" directory.

      :param: parsredArgs from ParseArg [OrderedDict]

      :return: 
	    userconfig  [config Dict] - written to file path shown in writefiles.log

      :raises: FatalError or partialError [Exception] or [error sink list]

      *user can re-run ipybuild on a partialError fix*

    '''
    parsedArgs = ndcDict(parsedArgs)
    config = None
    userconfig = None

    #load default "bank" config
    with open(defaultcfg, 'r') as jcr:
        config = json.load(jcr)
    log.FILE('Confirmed: {}'.format(defaultcfg))

    #assign paths
    config = AssignPaths(parsedArgs['configPath'],
                         parsedArgs['mainName'],
                         parsedArgs['json'],
                         parsedArgs['outDir'],
                         config)
   
    config['CONFIGPATH'] = os.path.abspath(config['CONFIGPATH']) 
    with open(config['CONFIGPATH'], 'w') as jcw:
        json.dump(config, jcw, indent=4)
    userconfig = ndcDict(config)
    log.FILE('{}'.format(userconfig['CONFIGPATH']))

    # assign input args
    uconfig = AssignArgsConfig(parsedArgs, userconfig)

    # check input args
    CheckConfig(uconfig)

    return ndcDict(uconfig)

def loadRes(arg):
    '''
       Check a filepath(s) and return path or list of paths

       :param: arg [str] or [list] - path to listfile of filepaths 

       :return: filepaths(s) [str] or [list]

    '''
    listOfFiles = []
    flst = None
    sepc = ','
    assert len(sepc) == 1, 'bad sepc format'
    if '[' in arg and sepc in arg:
        args = arg.replace('[', '').replace(']', '').split(sepc)
        for filelst in args:
            lfiles = None
            # open read
            lfiles = (openResListFiles(filelst))
            listOfFiles.append(lfiles)
        return listOfFiles
		
    flst = openResListFiles(arg)
    return flst

def openResListFiles(rpath):
    '''
	   #TODO always partial error in final recursive read as
	   #this last try read the text content and not a valid path.
	   #Even a regx match errors on "someClass.run" because it 
	   #looks like a path
       
	   Check if path is existing file or partial error

       :filters: .dll and .exe files to not read

       :param: rpath [str] - a file path 

       :return: [str] - path if isfile

       :raise: [IOError] sent to partialError
	   
    '''

    rpath = pathRead(rpath)    
    resfiles = None
    resFiles = None
    
    # arg exists as file
    if '.dll' not in rpath.lower() and '.exe' not in rpath.lower() and \
        '.py' not in rpath.lower():

        with open(rpath, 'r') as txtr:# errors on bad file | path
            resFiles = txtr.readlines()

    # chk list or str
    try:
        # None if not path
        if resFiles:
            resfiles = pathRead(resFiles)

    except IOError as ex:

        rname = os.path.basename(rpath)
        msg = ('\n Possible err(s) in:\n "{}": ' + \
               '\n - retrieved:\n' + '"\n\t{}"'*len(resFiles[:4]) + \
               '\n\tCheck if Bad File | Path *or* - \n' + \
               '\n\t"OK" if err shows "{rn:}"'+ \
               ' content text and not file path.' \
               '\n\t - Tried to read recursively into '+ \
               ' "{rn:}"\n\t - searching' + \
               ' for files.').format(rpath, *resFiles[:4], rn=rname)

        partialError(ex, msg)

    if resfiles:
        return resfiles
    return pathRead(rpath)

def _fmtResFiles(rfile):
    '''
       :param: rfile [str] - File like path
       
       :return: 
	       - valid path(s) [str] or [list]
           - else return None

    '''
    #string list of string
    sepc = ','
    assert len(sepc) == 1, 'bad spec format'
    if '[' in rfile and sepc in rfile:
        rfile  = rfile.replace('[', '').replace(']', '').split(sepc)
    fmt = None
    seps = [',', ';', '\n', '\r']
    assert len(seps[0]) == 1, 'bad format in seps'
    sep = []

    #strip leading whitespace
    if isinstance(rfile, (str, unicode)):
        sep = [sp for sp in seps if sp in rfile]
        if sep and rfile.count(sep[0]) > 0:
            fmt = _fmt_list(rfile.split(sep[0]))
        else:
            fmt = _fmt_str(rfile)
        return fmt

    #normal list in listfile
    if isinstance(rfile, list):
        fmt = _fmt_list(rfile)
    return fmt

def _fmt_list(lstfiles):
    '''
       Return cleaned valid paths like or Error

    '''
    rfiles = []
    seps = [',', ';', '\n', '\r']
    assert len(seps[0]) == 1, 'bad format in seps'
    sep = []
    for sfile in lstfiles:
        #no strip to conserve returns '\\nr'
        if not isinstance(sfile.strip(), (str, unicode)):
            continue

        sep = [sp for sp in seps if sp in sfile]
        if sep and sfile.count(sep[0]) > 0:
            for rf in sfile.split(sep[0]):
                if rf.strip():
                    rfiles.append(_fmt_str(rf.strip()))
        else:
            if sfile.strip():
                rfiles.append(_fmt_str(sfile.strip()))
    return rfiles

def _fmt_str(strfile):
    '''
      Clean a str like path and return or Error

    '''
    csep = ','
    assert len(csep) == 1, 'bad format in csep'

    sfile = opn(strfile)
    if  ',' in strfile:
        sfile = strfile.replace(',', '')

    if  '\\n' in strfile:
        sfile = strfile.replace('\\n', '')

    sfile = sfile.lstrip()
    #invalid list file assume source file
    if not _validateFileIsPath(sfile.strip()):
        sys.stdout.flush()
        raise IOError('file | filepath {} '.format(sfile))

    return sfile.strip()

def _validateFileIsPath(txt):
    '''
      Regex parse a valid filepath into path:name:ext group
	  
	  :param: txt [str] - vaild filepath
	  
	  :return: True [bool] - if '.' in matched group
	  
      # TODO may setup read fail on directory name like folder.myproj 
	   # where user/ipybuild forgot the file name.
	  
    '''
    regfilepathSplit = "^(.*/|.*\\\\)?(?:$|(.+?)(?:(\.[^.]*$)|$))" #ver2
    re_txt = re.compile(regfilepathSplit)

    if '.' in re_txt.findall(txt)[0][-1]:
        return True

    return None
