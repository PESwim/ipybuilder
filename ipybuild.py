# -*- coding: utf-8 -*-
'''
  **Version:** 0.0.A10 - |today|

  :created on: Wed Feb 14 19:44:03 2018
  :author: PE LLC peswin@mindspring.com
  :copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

  *space separated - use relative or absolute paths*
  *non-quoted args* - *no space in comma separated lists* 
     
  params:
  
  :configPath: [opt][str] - user .config path location or '' to use default_config.config 

  :mainName: [str] -  Python/IronPython ".py" file to compile as library .dll or .exe 
        
  :outDir: [opt][str] - output directory path - default "release/"

  :jsonarg: [opt][str] - path to assembly and embedding flags .json file
    
  :Bool or makeEXE=: True - make exe [bool][opt] - default False to make dll file
  
  :args: 
      - single file paths [str] to add in compile
      - MUST contain key word ('exe', 'dll', or 'zip') don't mix
      - like mypydll.py or zip.txt       
      
  **kwargs** filepath - like listexe=myprojectpyfilelist.txt [opt]
        
    :listexe or exe: - all .py required to run the main.py file as an exe 
    :listdll or dll: - pre-compiled .dlls or .py module files to add or embed in main
    :listzip or zip: - file path structure and file archive into output directory
    
  options: at end of params
  
  *  -h,/? help  
  
  *  -v verbose output
   
  *  *see help (-h -v) and documentation for more*  

  Example: ``python ipybuild.py c:/souredir/my.config appname c:/release
            listexe=c:/dev/include.txt``

'''

def helpVerbose():
    '''

       Writes or reads a python compile specific config file used in buildmake.py.
       Command-line args are parsed by pseudo-ORDER.

           First three args any order.
 
       args:
  
       :configPath: [opt][str] - user .config path location or '' to use default_config.config 

       :mainName: [str] -  python/ironpython ".py" file to compile as library .dll or .exe 

       :outDir: [opt][str] - output directory path - default "release/"

       :jsonarg: 
           - [opt][str] - path to assembly and embedding flags .json file
           - defaults to "defaults/"asembly_config.json" and requires the file path subdirectory "defaults/".

       :Bool or makeEXE=: True - make exe [bool][opt] - default False to make dll file

           After first three/four args above.
  
       :args: single file paths [str] to add in compile - MUST contain key word ('exe', 'dll', or 'zip') 
            - like mypydll.py or zip.txt       
      
       **kwargs** filepath - like listexe=myprojectpyfilelist.txt [opt]
                           - or "{'listexe':'myprojectpyfilelist.txt'}"
        
         :listexe or exe: - all .py required to run the main.py file as an exe 
         :listdll or dll: - pre-compiled .dlls or .py module files to add or embed in main
         :listzip or zip: - file path structure and file archive into output directory
    
       options 
  
       -h,/? help 
  
       **max output switch**: args include -v ex. -h -v

       -v verbose output 

       Example: ``python ipybuild.py c:/souredir/my.config appname.py c:/release
                listexe=c:/dev/include.txt``   

           **cmd example**:
             ``python ipybuild.py '' examples\makehello.py example\makehello
             _assembly.json 'True' 'listdll=examples\listdll.txt``

       names/outdir omitted are auto-named with the following preference;
       *assembly.json path >> main name path >> config name path*


       *help - extra*: -h, /h, /? plus -v

       **setup**: [opt]: manually setup "appname".json file: defaults to appname_assembly.json

       **assembly json**
         - User assembly info compiled into exe
         - User assembly info (i.e. version) - Not Implemented for dll files
         
         **assembly.json file content (default):**
         ..code-block: json::
           {
            "company": "Your Identifier"
            "product_version": "0.0.0.1"
            "standalone": false               / set true for exe standalone
            "file_version": "0.0.0.1"
            "embed": false                    / set true to add dlls to exe
            "libembed": false                 / set true to add StdLib.dll to exe
            "copyright": "Copyright Notice"
            "product_name": "Application exe name"
           }
       
        **args**:

   	     configPath [opt] - "" or  user config path ex. myapp.config
                   |[default] - UserDefaulted/default_config.config		 
         
         mainName - input main entry Name or dll Name ex. hello.py
                   |can build config but can't compile until provided
         
         bool or makeEXE [opt] = [True,False] - [default] False ex. True or makeExe=True
                   |Set/provide True arg for executable (exe)

         jsonp [opt] - path to assembly.json file
         
         outDir [opt]- output dir relative or absolute path

       **no comma separation unless inside tuple or list, no spaces k=v**

       **configPath**:
         - if args configuration path exists reads, otherwise writes then:
           creates "app_config.config used for main name "app".py.
         - *use two quotes, no space '' for a default config file*

       **extended args**: abs/rel paths
         :[opt]: listexe - path/ listexe.txt: exe inlcude module.py files
         :[opt]: listdll - path/ listdll.txt: dll inlcude files
         :[opt]: listzip - path/ listzip.txt: zip package files

       ipybuild maps input based on 'dll', 'exe', or 'zip' as part of the arg.

       **create include file lists create with an editor**: (listexe, listdll, listzip)::

         Do not mix:  bad       - listdll.zip, listdll=exedll.txt
                      good use  - listzip.txt
                                - listdll=my.py,your.py
                                - listdll=my.dll

       Can be one file or file list, comma or newline separated.
       Generate a list by a windows ``dir /b >> mylistdll.txt`` or
       bash ``ll >> mylistexe.txt`` command piped to file
       then edit to build/load exactly what you want and where it is located.

       **kwargs**: [opt]: any or all list file as key,value pair
       **result**: Reads/writes a user config file "mainName"_config.config
         Builds an exe or dll file based on options makeEXE

         Example: ``python ipybuild.py souredir/my.config sorcedir/appname.py c:/release
                    listexe=c:/dev/include.txt``
         Same as: ``python ipybuild.py souredir/my.config sorcedir/appname.py c:/release
                    c:/dev/include_exe.txt``
         Same as: ``python ipybuild.py 'sourcedir/my.config' 'source/appname.py'
                    c:/release' "{'listexe':'c:/dev/include.txt'}"``
					
      **update previous run with new param**: python ipybuild.py c:/souredir/my.config, "" c:/debug
      **see**: examples/ and examples/release
      **note**: Make sure your .py runs (ipy.exe) from release directory then all
        references should match the compiled ver. You don't have to
        keep the .py files in release, just use them to check.

        *If unittest was run *before* ipybuild you MUST restart
        the python interpreter to get logging in ipybuild runs.*

        *file write logs* can only be manually deleted after python interpreter is closed

        **Carefully read the output and File log to see find what is executing**

    '''
#  ** Set log level by INFO in buildlogs **
clr = None
import sys
try:
    import clr
    clr.AddReference("System")
    import System
except ImportError as ex:
    pass
if clr:
    try:
        clr.AddReference("StdLib")
    except System.IO.IOException as ex:
        print('StdLib.dll reference error:\n\t' + \
              'check file | filepath')
    try:
        clr.AddReference("ipybuild")
    except System.IO.IOException as ex:
        print('ipybuild reference error:\n\t' + \
              'check file | filepath')    
    if any(anarg in '-v' for anarg in sys.argv):
        print
        print 'clr refs'
        print
        print clr.References
        print

import json
import time
import copy
import logging
import required
from required import checkRequiredIP
import buildlogs
from buildlogs import dynfile

log = dynfile(__name__)
log.debug('\n---------------- ' + str(__name__) + \
              ' loaded -----------------')
#---------------------------- code width --------------------------------------
log.info('Checking paths, zip(if any), IronPython: ~30 sec (first run find IPY) to Compile start .....')
import makeload
from buildcheck import checkBuildConfig
from makeparse import MainParse, CommandLineParse
import filecontrol
from partialerror import PartialErrors
import globalstate
from globalstate import gsBuild
def Build(args):
    '''
       User normal call - provide filepaths and bool True to make exe
	                       args, kwargs have list or str of resources to add.
						      - For lists of resource files:
						        Associated py files in listexe.txt , .py or .dll
						        libraries in listdll.txt files files to zip in
                          listzip.txt.
                        - For single resources:
   						       just add the filepath; listexe=module.py.

       :params: configPath, mainName, outDir,
                jsonp, makeEXE, *args, **kwargs

       :return: None

       :output: Status and build files

    '''
    checkhelp(args)
    checkRequiredIP()
    if gsBuild.Verbose or not gsBuild.INFO:
        log.info('\nInput args:\n {}'.format(json.dumps(args),indent=4))
    CmdConfig(args)

    return True

def ScriptBuild(configPath=None, mainName=None, outDir=None,
                jsonp=None, makeEXE=False, *args, **kwargs):
    '''
       User normal call - see Build

       :params: configPath=None, mainName=None, outDir=None,
                jsonp=None, makeEXE=False, *args, **kwargs

       :return: None

       :output: Status and build files

    '''
    checkRequiredIP()
    margs = (configPath, mainName, outDir, jsonp, makeEXE, args, kwargs)
    uargs = MainParse(*margs)
    uconfig = makeload.LoadConfig(uargs)
    checkBuildConfig(uconfig)
    Results(uconfig)

    return True

def Results(cnfg):
    '''
       Formatted Build Output

       :param: config [dict]

       :output: [PartialErrors] partial errs - try and let ipybuild run

    '''
    #TODO keep recursive reading from throwing partial error
    if PartialErrors:
        log.info('\nOK - Usually Partial Errors allow complete build ' + \
                 'wtih the follwoing errors related to recursive reading:\n')

        for i, err in enumerate(PartialErrors):
            print('*ERR -{} {}\t\n  Traceback -\n\t {}' \
                  .format(i, err[0], err[1]))

        log.warn('\nRe-run ipybuilder *if* required - ' + \
                 'check errs and type - update or fix.')
    if gsBuild.Verbose or not gsBuild.INFO:    
        log.info('\nlogging to file:\n {}' \
                 .format(str(logging.getLogger('').handlers[0].stream.name)))

    if not PartialErrors:
        log.info('\nBuild state OK')

def MainConfig(configPath=None, mainName=None, outDir=None,
               jsonp=None, makeEXE=False, *args, **kwargs):
    '''Unittest intermediates - used for intermediate output checks'''
    log.FILE('______________' + \
                     str(time.strftime('%x %X', time.localtime())) + \
                           '____________')
    margs = (configPath, mainName, outDir, jsonp, makeEXE, args, kwargs)
    uargs = MainParse(*margs)
    uconfig = makeload.LoadConfig(uargs)
    checkBuildConfig(uconfig)#, show=True)
    ResultCap(uconfig)
    return uargs

def CmdConfig(args):
    '''Unittest intermediates'''
    args = copy.copy(args)
    uargs = CommandLineParse(args)
    uconfig = makeload.LoadConfig(uargs)
    checkBuildConfig(uconfig)#, show=True)
    Results(uconfig)
    return uargs

def ResultCap(cnfg):
    '''
       Unit test captured output called in MainConfig.
       Test content in unittest - test captures output

       :param: config [dict]

       :oupt: partial errs [PartialErrors]

    '''
    print('---------   START: capture output for unittest ----------')
    from partialerror import nullPartialErrors

    if PartialErrors:
        print('\nPartial configuration completed wtih the follwoing ' + \
                 'errors:\n')
        for i, err in enumerate(PartialErrors):
            print('*ERR -{} {}\t\n  Traceback -\n\t {}' \
                  .format(i, err[0], err[1]))
        print('\n *Re-run ipybuilder as required - ' + \
              'check errs and type - update or fix.')

    if not PartialErrors:
        print('\nBuild state OK')

    print('---------   END: capture output for unittest ------------')

    nullPartialErrors()
    
def checkhelp(args):
    
        if any(arg in ['/?', '/h', '-h', '-help', 'help'] for arg in args):
            if gsBuild.Verbose:
                print(sys.modules['__main__'].helpVerbose.__doc__)    
            else:
                print(sys.modules['__main__'].__doc__)
            raise SystemExit(0)

def logReport():
    '''
      Output filtered log files showing:
        - files confirmed to exists during run
        - files written during run

      :log error: Unit testing run before ipybuild kills ipybuild logging

    '''
    writelog = None
    curDateTime = time.strftime('%x %X', time.localtime())
    all_log = list(filecontrol.getWriteLog())
    writelog = filecontrol.getFilesWritten(all_log)
    confirmed = filecontrol.getFilesConfirmed(all_log)
    # debug or check required
    #    exists = [flog for flog in all_log \
    #              if 'Exists' in flog and not '____' in flog]
    
    log.info('\n\t   time {}'.format(curDateTime))
    if not writelog:
        log.error('\nUNITTEST WAS RUN BEFORE IPYBUILD ' + \
                  '- NO FILE LOGGING - RESTART RUN IPYBUILD ')
    if writelog:
        if gsBuild.Verbose or not gsBuild.INFO:
            log.info(('\nwrite log:' + '\n {}'*len(writelog)) \
                     .format(*writelog))
    if confirmed:
        if gsBuild.Verbose or not gsBuild.INFO:
            log.info(('\nconfirmed log:' + '\n {}'*len(confirmed)) \
                     .format(*confirmed))

if __name__ == '__main__':
    ret = None 	#always uncommented
#     LEAVE commented unless you want to run examples below
#    *Uncomment parts to run script Examples*
#    - make sure files are in the eamples directory-
#*********************debug ***************************************
#    "need the first set of '' to represent the real cmd-line first arg (module)
#     always put in sys,argv by python interpreter." Second set of quotes is a
#     user's arg requesting  to use the default configpath arg."

#    sys.argv = ['', '', 'UserDefaulted/ipybuild.py', 'assembly.json', 'True',
#                '../install/debug' 'listexe=../install/listexe.txt',
#                'listzip=..\install\listzip.txt']

# -------   cmdline Build run --------

#    sys.argv = ['','', 'examples\makehello.py','examples/cmd',
#                'examples\make_assembly.json', 'True',
#                'listdll=examples\listdll.txt'
#               ]

    #MUST RUN ABOVE TO MAKE /CMD first
#    sys.argv = ['','', 'examples\makehelloembed.py',
#                'examples\makehelloself_assembly.json', 'True',
#                'examples\cmdlib', 'listdll=[examples\cmd\make.dll,' + \
#                ' examples\cmd\ipyver.dll'
#               ]

# --- always uncommented --
    if len(sys.argv) > 1:

        try:
            ret = Build(sys.argv)
        except SystemExit as ex:
            ret = -1
            if str(ex) != '0':
                print(ex)

    elif len(sys.argv) == 1:
        #  ------  debug/show how to use ipver with clr ------
#        from globalstate import gsBuild
        if not gsBuild.INFO and clr:
#            import globalstate
            import ipyver
            try:
                clr.AddReference("System")
                import System
            except System.NotSupportedException as  ex:
                print(ex)

            rs = ipyver.ReferenceStatus('globalstate').RefStatus()
            print('\nShowing example using ipyver for "globalstate" import.')
            for k, v in rs.iteritems():
                print('{} : {}'.format(k ,v))
        #	------- comment out above -----------------
        #pass

# -------   scrip ScriptBuild run (comment out ipyver, pass above) ------
#        ret = ScriptBuild(' ', 'examples\make.py',
#                          'examples\make_assembly.json',
#                          True, 'listdll=examples\listdll.txt')
#        ret = ScriptBuild(' ', 'examples\makehelloself.py',
#                          'examples\makeself_assembly.json',
#                          True, 'listdll=[examples\makes.py,ipyver.py]')
#   always uncommented
    if not ret:
       print('Echo no params - OK')

    elif ret != -1:
        logReport()

#   -------------------