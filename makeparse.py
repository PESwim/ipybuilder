# -*- coding: utf-8 -*-
"""
.. created on Wed Feb 14 19:37:02 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""
from version import __version__
import sys
from collections import OrderedDict
from buildlogs import dynfile
import ast
from partialerror import FatalError

log = dynfile(__name__)
log.debug('\n---------------- ' + str(__name__) + \
          ' loaded ----------------')
from makedefault import maindict, ndcDict #default,

def MainParse(configPath=None, mainName=None, outDir=None,
              jsonarg=None, makeEXE=False, *args, **kwargs):

    args_ = (configPath, mainName, outDir, jsonarg, makeEXE, args, kwargs)

    mainargs = ParseArgs(*args_)
    return mainargs

def CommandLineParse(arguments):
    '''
      *space separated - use relative or absolute paths*
      *non-quoted args*
      
      :configPath: user .config path or '' to use default_config.config [str] [opt]

      :mainName: python/ironpython .py file to compile as library .dll or .exe [str] [opt]
        - if you leave mainName out final compile is suspended until re-run with mainName

      :outDir: path output directory [str] [opt] = default "release/"

      :jsonarg: path to assembly and embedding flags .json file [str] [opt]
        - defaults to "defaults/"asembly_config.json" and requires the file path 
        subdirectory "defaults/".

      :makeEXE: True - make exe [bool] [opt] - default False to make dll file

      :args: single file paths [str] to add in compile - MUST contain key word ('exe', 'dll', or 'zip') 
        - like mypydll.py or zip.txt       
      
      **kwargs** filepath - like listexe=myprojectpyfilelist.txt [opt] 
        
        :listexe: - all .py required to run the main.py file as an exe 
        :listdll: - pre-compiled .dlls or .py module file to add or embed in main
        :listzip: - file path structure and file archive into output directory
       
      *see help (-h -v) and documentation for more*
      
    '''
    args = tuple(arguments[1:])
    comargs = ParseArgs(*args)

    return comargs

def _parseStd(*args):
    '''
      Separate str args, from tuple,lists,and kwargs
      :return: [dict] with keys ['s'] - single and ['d'] - multiple k,v

    '''
    sargs = args[0] #unpack
    argtyps = {'s':[],
               'd':{'listexe':None,
                    'listdll':None,
                    'listzip':None,
                    'makeEXE':False
                   }}
    lists = ['listexe', 'listdll', 'listzip', 'makeEXE']
    argtyps, lists = _parseTup(sargs, argtyps, lists)

    return ndcDict(argtyps)

def _parseDics(dickey, val, argtypes):
    ''' 
	   Handle dict parsing - [str] or [list] - into argtyps <type>
	
	'''

    atyps = ndcDict(argtypes)
    curdic = atyps['d'][dickey]

    if isinstance(curdic, list):
        atyps['d'][dickey].append(val)

    elif not curdic:
        atyps['d'][dickey] = val

    else:
        curval = curdic
        atyps['d'][dickey] = []
        atyps['d'][dickey].extend([curval, val])

    return ndcDict(atyps)

def _parseOrder(argtyps):
    '''
       Order args by type of content (literal).
       *i.e.* **".py"** *in arg --> place in mainName as python file.*
       :return: agrtyps [ordered dict]

    '''
    argtyps = ndcDict(argtyps)

    # filter config, name, json assembly
    if argtyps['s']:
        argslst = list(argtyps['s'])
        argtmp = [None, None, None, None]
        for ar in argslst:
            if ar:
                if '.config' in ar:
                    argtmp[0] = ar
                elif '.py' in ar:
                    argtmp[1] = ar
                elif (ar.startswith('/') or ar.startswith('\\') and \
                    not '.' in ar) or (ar.endswith('/') or ar.endswith('\\')):
                    argtmp[2] = ar
                elif '.json' in ar:
                    argtmp[3] = ar
                
        if not argtmp[0]:
            argtmp[0] = ' '

        alst = list(argslst)
        tmplst = []
        for i, s in enumerate(alst):
            if s and s not in argtmp:
                tmplst.append(s)
        tmplst = list(tmplst[::-1])
        for j, a in enumerate(argtmp):
            if not a and tmplst:
                argtmp[j] = tmplst.pop()
        argtyps['s'] = None
        argtyps['s'] = argtmp

    return argtyps

def ambigWarn(arg):

    log.warn(
        ('\nAmbiguous paramaters - need more filepath information:' +
         '\ncould not correctly parse - skipped:\n\t {}\n' +
         '\n\t *Use resource lists names: "listexe", "listdll", "listzip"' +
         '."txt"' +
         '\n\t *Param name like "programdll.zip" has 2 types "dll" and "zip"' +
         '\n\t *Use param name like "./myzip.zip" in tuple ("./myzip.zip")' +
         '\n\t\t or use "listzip = ./myzip.zip"') \
             .format(arg))

def _parseTup(tup, argtyps, lists, f_list=False):
    '''
       Handle tuple arg parsing into argtyps <type>
	   
	'''
    tags = ['exe', 'dll', 'zip']
    trylst = None
    f_brokenlst = False
    for arg in tup:
        if arg and '[' in arg and ']' not in arg and not f_brokenlst:
            trylst = arg
            log.info('\nlist paramater {} was not quoted.'.format(arg))
            f_brokenlst = True
            continue

        elif trylst  and ']' in arg and '[' in trylst and f_brokenlst:
            arg = trylst + arg
            log.info('\npatched paramater now: {}'.format(arg)) 
        elif trylst:
            log.error('need to quote lists, tuples, dicts in input parameters')
            
        try:
            arg = ast.literal_eval(arg)
        except Exception:
            pass

        tagmatch = None
        key = None
        dkey = None
        keys = None
        dkeys = None
        if arg:
		
            #Only get here on "True" - Must handle bool first or error
            if isinstance(arg, bool):
                argtyps['d']['makeEXE'] = arg
                lists.remove('makeEXE')
                continue
            keys = [k for k in lists if k in arg]
            ms = [m for m in tags if m in arg]
            if keys and len(keys) > 1 or (ms and len(ms) > 1):
                ambigWarn(arg)

            if keys:
                key = keys[0]

            tagmatches = [m for m in tags if m in arg]
            if tagmatches:
                tagmatch = tagmatches[0]
                dkeys = [dk for dk in lists if tagmatch in dk]
            if dkeys:
                dkey = dkeys[0]

            if isinstance(arg, (str, unicode)) and '=' not in arg:
                #put in first match
                if key:
                    argtyps['d'][key] = arg
                    continue

                elif not key and not tagmatch and not f_list:
                    argtyps['s'].append(arg)
                    continue

                elif not key and not tagmatch and f_list:
                    argtyps = _parseDics('listexe', arg, argtyps)
                    continue

                elif tagmatch:
                    argtyps = _parseDics(dkey, arg, argtyps)
                    continue
                else:
                    ambigWarn(arg)
                    raise FatalError('ValueError',
                                     'Error: Ambiguous param: ' + \
                                     str(arg))

            elif isinstance(arg, (str, unicode)) and '=' in arg:
                if (key and key in arg.split('=')[0]) or dkey:
                    if not key and dkey:
                        key = dkey
                    argtyps = _parseDics(key, arg.split('=')[1], argtyps)
                else:
                    ambigWarn(arg)
                    raise FatalError('ValueError',
                                     'Error: Ambiguous param: ' + \
                                     str(arg))
            elif isinstance(arg, dict):
                for k, v in arg.iteritems():
                    argtyps = _parseDics(k, v, argtyps)

            elif arg and isinstance(arg, list) or \
                   isinstance(arg, tuple):
                argtyps, lists = _parseTup(arg, argtyps, lists, True)

    argtyps = ndcDict(_parseOrder(argtyps))

    return argtyps, lists

def ParseArgs(*sargs):
    '''
       Parse cmd or script args with ability
       to parse/accept multiple user type entries.
       :return: user args [ordered dict]

    '''
    argtypes = _parseStd(sargs)
    mainargs = OrderedDict(maindict)
    mkeys = mainargs.keys()

    for ky, vl in argtypes.iteritems():
        if ky == 's':
            for i, p in enumerate(vl):
                mainargs[mkeys[i]] = p
        if ky == 'd':
            mainargs.update(argtypes[ky])

    return ndcDict(mainargs)

if __name__ == '__main__':
    pass
