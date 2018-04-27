# -*- coding: utf-8 -*-
"""
.. created on Wed Feb 14 19:40:02 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""
from version import __version__
import os
from os import path as op
from os.path import abspath as opab
from os.path import join as opj
from os.path import normpath as opn
from os.path import dirname as opd
from os.path import basename as opb
from os.path import exists as opex
from os.path import isdir as opisd
from ipyrequirements import REQUIREMENTS as ipyreq
import re
from copy import deepcopy
from collections import OrderedDict
import json
import unittest
from regt import SlashContrl
from buildlogs import dynfile
from globalstate import gsBuild

log = dynfile(__name__)
log.debug('\n---------------- ' + str(__name__) + \
              ' loaded --------------')
if not opex(opn(opab(opj(os.getcwd(),'defaults')))):
    print('no exist {}'.format(opn(opab(opj(os.getcwd(),'defaults\\')))))
    try:
        os.mkdir(opn(opab(opj(os.getcwd(),'defaults'))))
    except Exception as ex:
        print(ex)
        
#opn is key to run in clr?    
defaultcfg = opn(opj(os.getcwd(), 'defaults\\default_config.config'))
defaultjson = opn(opj(os.getcwd(), 'defaults\\default_assembly.json'))

if 'Tests' in os.getcwd():
    defaultjson = opj(opd(os.getcwd()), 'defaults\\default_assembly.json')
    defaultcfg = opj(opd(os.getcwd()), 'defaults\\default_config.config')

defaultconfig = {'MAKEEXE'    : False,
                 'MAKEDIR'    : None,
                 'OUTDIR'     : None,
                 'MAINFILE'   : None,
                 'LISTFILES'  : {'exe':[None],
                                 'dll':[None],
                                 'zip':[None]},
                 'JSONPATH'   : None,
                 'ASSEMBLY'   : {"standalone":False,
                                 "embed":False,
                                 "libembed": False,
                                 "company":None,
                                 "product_version":None,
                                 "product_name":None,
                                 "copyright":None,
                                 "file_version":None},
                 'CONFIGPATH'  :None,
                 'ZIPPATH'     :None,
                }

if not os.path.exists(defaultcfg):
    with open(defaultcfg, 'w') as jcw:
        json.dump(defaultconfig, jcw, indent=4)
    log.FILE('{}'.format(defaultcfg))
    log.info('\nExisting resource not found wrote default config:\n {}'\
            .format(defaultcfg))

maindict = OrderedDict([('configPath', defaultcfg), ('mainName', None),
                        ('outDir', None), ('json', None), ('makeEXE', False),
                        ('listexe', None), ('listdll', None),
                        ('listzip', None)])

assembly_json = {"standalone":False, "embed":False, "libembed": False,
                 "company":None, "product_version":None, "product_name":None,
                 'copyright':None, 'file_version':None}

if not os.path.exists(defaultjson):
    with open(defaultjson, 'w') as jassw:
        json.dump(assembly_json, jassw, indent=4)

    log.FILE('{}'.format(defaultjson))
    log.info('\nExisting resource not found wrote default assembly:\n {}' \
             .format(defaultjson))

DefaultReq = ipyreq
DefaultReqList = []
for txtPath in DefaultReq:
    if gsBuild.IPATH:
        DefaultReqList.append(opn(opj(gsBuild.IPATH,
                                      opb(opn(txtPath.strip())))))
#    elif gsBuild.IPATH == 'clr':
#        DefaultReqList = []
#        DefaultReq = []
    else:
        DefaultReqList.append(os.path.normpath(txtPath.strip()))
        
DefaultReqPath = opn(opj(os.getcwd(),'requirements.txt'))

with open(DefaultReqPath, 'w') as tw:
          tw.writelines(('\n').join(DefaultReqList))

if opex(DefaultReqPath):
    log.FILE('Exists {}'.format(DefaultReqPath))

#else:
#    with open(DefaultReqPath, 'w') as tw:
#        tw.writelines(('\n').join(DefaultReqList))
#    if opex(DefaultReqPath):
#        log.FILE('{}'.format(DefaultReqPath)) 
        
if opex(opn(opab(opj(os.getcwd(),'defaults\\ipath.txt')))):
   with open(opn(opab(opj(os.getcwd(),'defaults\\ipath.txt'))), 'r') as tr:
       gsipath = tr.readline().strip()
       
   if opex(gsipath) or gsipath == 'clr':
      gsBuild.IPATH = gsipath

   else:

      try: 
          os.remove(opn(opab(opj(os.getcwd(),'defaults\\ipath.txt'))))
      except Exception as ex:
        pass              
#---------------------------- code width --------------------------------------

def ndcDict(rdic):
    ndict = None
    if isinstance(rdic, OrderedDict):
        ndict = OrderedDict()
        #TODO check deepcopy
        ndict.update((k, v) for k, v in rdic.iteritems())
    elif isinstance(rdic, dict):
        ndict = dict(deepcopy(rdic))
    return ndict

def validatePath(txt):
    '''
      Regex parse a valid filepath into path:name:ext group
      
	  :param: txt [str] - valid file path
	  
	  :return: path:name:ext [list] or []
	  
    '''
    regfilepathSplit = "^(.*/|.*\\\\)?(?:$|(.+?)(?:(\.[^.]*$)|$))" #ver2
    re_txt = re.compile(regfilepathSplit)

    return re_txt.findall(txt)

def BasePathDir(dp):
    '''
       Parse a file path and return dict of info about path

       :param: dp [str] - user arg path
	
       :return:
           - (main, base, basetype, isFile, isdefault) [tuple] 
           - main [str] - fullpath parent
           - base [str] - base of path dir or file path
           - basetype [basetype [python, json, config, None]]
           - isFile [bool]
           - isdefault [ bool] - True if output is going to UserDefaulted/

	'''
	
    dp = dp.strip()
    base = None
    main = None
    dpex = op.exists(opab(dp))
    main = opd(dp)
    mainex = op.exists(main)
    base = opb(dp)
    hasdot = '.' in base
    basetype = None
    isFile = False
    isdefault = False

    if dpex:
        isFile = op.isfile(opab(dp))

    if hasdot:
        if '.py' in base:
            basetype = 'python'
        elif '.json' in base:
            basetype = 'json'
        elif '.config' in base:
            basetype = 'config'

    if (opb(main)) == 'builder':
        main = opn(opj(main, 'UserDefaulted'))
        isdefault = True

    if not hasdot and base == opd(main):
        return (main, None, None, isFile, isdefault)

    elif not hasdot and base in os.getcwd():
        if base == 'builder':
            base = opn(opj(base, 'UserDefaulted'))
            isdefault = True
        return(opn(opj(opab(main), base)), None, None, isFile, isdefault)

    elif not mainex:
        if op.exists(opn(opab(opd(main)))):
            isdefault = True
            return(opn(opj(opab(opd(main)), 'UserDefaulted')),
                   base, basetype, isFile, isdefault)
        isdefault = True
        return(opn(opab(opj(opd(main), 'UserDefaulted'))),
               base, basetype, isFile, isdefault)

    return(main.strip(), base.strip(), basetype, isFile, isdefault)

def SlashArgs(config, name, jsn, out):
    '''
      Runs SlashControl and BasePath for each user path arg:
       
	   :params: (configPath, mainName, jsonp, outDir)
       
	   :return: (argc, argm, argj, argo) [tuple]
	   
    '''
    argc = argm = argj = argo = None

    if config == ' ':
        config = None
    if config:
        config = SlashContrl(config)
        argc = BasePathDir(config)
    if name:
        name = SlashContrl(name)
        argm = BasePathDir(name)
    if jsn:
        jsn = SlashContrl(jsn)
        argj = BasePathDir(jsn)
    if not out or out == '' or  out == ' ':
        if argm and argm[0]:
            out = argm[0] + '\\release'
        elif 'builder' == opb(opd(os.getcwd())):
            out = os.getcwd() + '\\UserDefaulted\\release'
        else:
            out = os.getcwd() + '\\release'

    out = SlashContrl(out)
    if not op.isdir(out):
        if not op.isdir(opd(out)):
            os.mkdir(opd(out))
            log.FILE('{}'.format(opd(out)))

        if not op.isdir(out) and not op.isfile(out):
            os.mkdir(out)
            log.FILE('{}'.format(out))

    argo = BasePathDir(out)
    return (argc, argm, argj, argo)

def setMkdir(argc, argm, argj):

    if argm:
        mkdirp = argm[0]
    elif argj:
        mkdirp = argj[0]
    elif argc:
        mkdirp = argc[0]
    else:
        mkdirp = opn(opj(os.getcwd(), 'UserDefaulted'))
    return mkdirp

def setConfig(configPath, mainName, jsonarg, argc, argm, argj):
    '''
      Path json with assembly >> main >> if config None

    '''

    basem = None
    basec = None
    basej = None
    mainp = None
    jsonp = None
    configp = None

    if argc:
        configp, basec, typc, isFilec, isdefaultc = argc

    if basec and '.' in basec and '.config' in basec:
        configp = opn(opj(configp, basec))

    elif basec and '.' in basec:
        if isdefaultc:
            configp = opn(opj(configp, ('.').join(basec.split('.')[:-1])) + \
                              'default_config.config')
        else:
            configp = opn(opj(configp, ('.').join(basec.split('.')[:-1])) + \
                              '_config.config')

    elif basec and basec != op.basename(os.getcwd()):
        configp = opn(opj(configp, basec) + 'default_config.config')

    elif jsonarg:
        argj = BasePathDir(jsonarg)
        jsonp, basej, typj, isFilej, isdefaultj = argj
        configp = opn(opj(jsonp, ('.').join(basej \
                          .split('.')[:-1])) + '_config.config')
    elif mainName:
        mainp, basem, typm, isFilem, isdefaultm = argm

        if basem and '.' in basem:
            basem = ('.').join(basem.split('.')[:-1]) + '_config.config'
        elif basem and basem != op.basename(os.getcwd()):
            configp = opn(opj(mainp, basem) + '_config.config')
        else:
            configp = opn(mainp + 'default_config.config')

    if not configp:
        configp = opj(os.getcwd(), 'UserDefaulted',
                      'default_config.config')
    return configp

def setMain(configPath, mainName, jsonarg, argc, argm, argj):
    '''
       path json with assembly >> main >> if config None
       reset mainName path to outDir if no arg "outDir"

    '''
    basem = None
    basec = None
    basej = None
    mainp = None
    jsonp = None
    configp = None

    if argc:
        configp, basec, typc, isFilec, isdefaultc = argc
    if argm:
        mainp, basem, typm, isFilem, isdefaultm = argm

    # json with assembly >> main >> if config None
    if isdefaultm:
       raise IOError('file | filepath not resolved:\n\t' + \
                     'Python type "main" .py file')

    if basem and '.' in basem and '.py' in basem:
        mainp = opn(opj(mainp, basem))

    elif basem and '.' in basem and basec:
        mainp = opn(opj(mainp,
                        ('.').join(basec.split('.')[:-1])) \
                             .replace('_config', '') + '.py')

    elif basem and basem != op.basename(os.getcwd()):
        mainp = opn(opj(mainp, basem) + '.py')

    elif jsonarg:
        jsonp, basej, typj, isFilej, isdefaultj = argj
        mainp = opn(opj(jsonp,
                        ('.').join(basej \
                        .split('.')[:-1])) + '.py')

    elif configPath:
        configp, basec, typc, isFilec, isdefaultc = argc

        if basec and '.' in basec:
            basec = ('.').join(basec \
                         .split('.')[:-1]) \
                         .replace('_config', '') + '.py'

        elif basec and basec != op.basename(os.getcwd()):
            mainp = opn(opj(configp, basec.replace('_config', '')) + '.py')

    if mainp:
        return mainp

    raise IOError('file | filepath not resolved:' +
                  '\n\t - No main python.py file')

def setPath(configPath, mainName, jsonarg, argout, f_type='json'):
    ''' Well this doesn't end - way too complex '''
    #TODO auto-fix file re-naming on err fix

    basem = None
    basec = None
    basej = None
    mainp = None
    jsonp = None
    configp = None

    odir = None
    argc, argm, argj, argo = SlashArgs(configPath, mainName, jsonarg, argout)

    if f_type == 'mkdir':
        return setMkdir(argc, argm, argj)

    odir = opn(opj(argo[0], argo[1]))
    if f_type == 'odir':
        return  odir

    if argc:
        configp, basec, typc, isFilec, isdefaultc = argc

    if configPath and f_type == 'config':
        return setConfig(configPath, mainName, jsonarg, argc, argm, argj)

    if argm:
        mainp, basem, typm, isFilem, isdefaultm = argm

    if mainName and f_type == 'name':
        return setMain(configPath, mainName, jsonarg, argc, argm, argj)

    if argj:
        jsonp, basej, typj, isFilej, isdefaultj = argj

    if mainName and f_type == 'json':
        if basec and '.' in basec:
            basec = ('.').join(basec.split('.')[:-1]).replace('_config', '')

    if basem and '.' in basem:
        basem = ('.').join(basem.split('.')[:-1])
        mainName = opn(opj(mainp, basem))

        if configp and not op.exists(mainp):
            mainName = opn(opj(configp.replace('_config', ''), basem))

    if jsonarg and f_type == 'json' and \
        op.basename(jsonarg) != 'default_assembly.json':

        if typj != 'json' and '.' in basej:
            basej = ('.').join(basej.split('.')[:-1]) #+ '_assembly.json'
        elif typj != 'json':
            basej = basej + '_assembly.json'
        if isFilej:
            jsonp = opn(opj(jsonp, basej))
        elif basej and not isdefaultj:
            jsonp = opn(opj(jsonp, basej))
        elif basej and mainp and not isdefaultm:
            jsonp = opn(opj(mainp, basej))
        elif basej and configp and not isdefaultc:
            jsonp = opn(opj(configp, basej))
        elif basej and mainp:
            jsonp = opn(opj(mainp, basej))
        elif basej and jsonp:
            jsonp = opn(opj(jsonp, basej))
        elif basej and configp:
            jsonp = opn(opj(mainp, basej))

        if jsonp:
            return jsonp
        else:
            jsonp = None

    if f_type == 'json':
        #falling backwards
        fallp = None
        if basem:
            basem = basem + '_assembly.json'
        defbase = 'default_assembly.json'

        if basem and mainp and op.exists(mainp) and not isdefaultm:
            fallp = opn(opj(mainp, basem))
        elif basem and configp and op.exists(configp):
            fallp = opn(opab(opj(configp.replace('_config', ''), basem)))
        elif basem and not configp and mainp:
            fallp = opn(opj(mainp, basem))
        elif configp and op.exists(configp):
            fallp = opn(opj(configp.replace('_config', ''), defbase))
        else:
            fallp = opn(opab(opj('./UserDefaulted', defbase)))
            
        return fallp

#pylint: disable=attribute-defined-outside-init
#pylint: disable=invalid-name
class TestCaseJson(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cwd = os.getcwd()
        cls.params = \
            [(None, './test.py', None, None),
             (None, '../test.py', None, None),
             (None, '.\\Tests\test.py', None, None),
             (None, 'Best\test.py', None, None),

             (cls.cwd, './test.py', None, None),
             (cls.cwd, '../test.py', None, None),
             (cls.cwd, '.\\Tests\test.py', None, None),
             (cls.cwd, 'Best\test.py', None, None),

             (cls.cwd+'\\Tester', './test.py', None, None),
             (cls.cwd+'\\Tester\\tester_config.config', '../test.py', None, None),
             (os.path.dirname(cls.cwd), '.\\Tests\test.py', None, None),
             (os.path.dirname(cls.cwd)+'/Tester', 'Best\test.py', None, None),

             (cls.cwd+'/default_config.config', 'Test\test.py', 'tester', None),
             (cls.cwd, '.\\Tests\test.py', 'test_assembly.json', None),
             (os.path.dirname(cls.cwd)+'/Tester', 'Best\test.py', 'tryjson', None),
             (cls.cwd+'\\Tests\\make_config.config', 'Best\test.py',
              'test_assembly.json', None),

             (cls.cwd+'/default_config.config', None, 'tester', None),
             (cls.cwd+'\\Tests\\make_config.config', None,
              'test_assembly.json', None),

             (None, None, 'test_assembly.json', None),
             (None, None, 'tryjson', None)
            ]

        cls.results = \
            [cls.cwd+'\\UserDefaulted\\test_assembly.json',
             os.path.dirname(cls.cwd)+'\\test_assembly.json',
             cls.cwd+'\\Tests\\test_assembly.json',
             cls.cwd+'\\UserDefaulted\\test_assembly.json',

             cls.cwd+'\\UserDefaulted\\test_assembly.json',
             os.path.dirname(cls.cwd)+'\\test_assembly.json',
             cls.cwd+'\\Tests\\test_assembly.json',
             cls.cwd+'\\UserDefaulted\\test_assembly.json',

             cls.cwd+'\\UserDefaulted\\test_assembly.json',
             os.path.dirname(cls.cwd)+'\\test_assembly.json',
             cls.cwd+'\\Tests\\test_assembly.json',
             os.path.dirname(cls.cwd)+'\\test_assembly.json',

             cls.cwd+'\\UserDefaulted\\tester_assembly.json',
             cls.cwd+'\\Tests\\test_assembly.json',
             os.path.dirname(cls.cwd)+'\\tryjson_assembly.json',
             cls.cwd+'\\Tests\\test_assembly.json',

             cls.cwd+'\\UserDefaulted\\tester_assembly.json',
             cls.cwd+'\\Tests\\test_assembly.json',

             cls.cwd+'\\UserDefaulted\\test_assembly.json',
             cls.cwd+'\\UserDefaulted\\tryjson_assembly.json',

            ]

        cls.test_results = \
            [os.path.dirname(cls.cwd)+'\\Tests\\test_assembly.json',
             os.path.dirname(cls.cwd)+'\\UserDefaulted\\test_assembly.json',
             cls.cwd+'\\UserDefaulted\\test_assembly.json',
             cls.cwd+'\\UserDefaulted\\test_assembly.json',

             cls.cwd+'\\test_assembly.json',
             cls.cwd+'\\UserDefaulted\\default_assembly.json',
             cls.cwd+'\\UserDefaulted\\default_assembly.json',
             cls.cwd+'\\UserDefaulted\\default_assembly.json',

             cls.cwd+'\\test_assembly.json',
             cls.cwd+'\\UserDefaulted\\test_assembly.json',
             os.path.dirname(cls.cwd)+'\\UserDefaulted\\test_assembly.json',
             os.path.dirname(cls.cwd)+'\\UserDefaulted\\test_assembly.json',

             cls.cwd+'\\tester_assembly.json',
             cls.cwd+'\\test_assembly.json',
             cls.cwd+'\\tryjson_assembly.json',
             cls.cwd+'\\test_assembly.json',

             cls.cwd+'\\tester_assembly.json',
             cls.cwd+'\\test_assembly.json',

             cls.cwd+'\\test_assembly.json',
             cls.cwd+'\\tryjson_assembly.json',

            ]

        if 'Tests' in cls.cwd:
            cls.results = cls.test_results

        print('\t setUpClass - ' + cls.__name__)
    def setUp(self):
        print("\n set-up " +  self.id())

    def tearDown(self):
        print("\ntear-down " +  self.id())

    def runTest(self):
        pass
    #@unittest.skip('less verbose debug')
    def test_case_json_m0(self):
        args = self.params[0]
        rslt = self.results[0]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_m1(self):
        args = self.params[1]
        rslt = self.results[1]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_m2(self):
        args = self.params[2]
        rslt = self.results[2]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_m3(self):
        args = self.params[3]
        rslt = self.results[3]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_4cm(self):
        args = self.params[4]
        rslt = self.results[4]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_5cm(self):
        args = self.params[5]
        rslt = self.results[5]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_6cm(self):
        args = self.params[6]
        rslt = self.results[6]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_7cm(self):
        args = self.params[7]
        rslt = self.results[7]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_8cm(self):
        args = self.params[8]
        rslt = self.results[8]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_9cm(self):
        args = self.params[9]
        rslt = self.results[9]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_10cm(self):
        args = self.params[10]
        rslt = self.results[10]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_11cm(self):
        args = self.params[11]
        rslt = self.results[11]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_12cmj(self):
        args = self.params[12]
        rslt = self.results[12]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_13cmj(self):
        args = self.params[13]
        rslt = self.results[13]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_14cmj(self):
        args = self.params[14]
        rslt = self.results[14]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_15cmj(self):
        args = self.params[15]
        rslt = self.results[15]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_16cj(self):
        args = self.params[16]
        rslt = self.results[16]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_17cj(self):
        args = self.params[17]
        rslt = self.results[17]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_18j(self):
        args = self.params[18]
        rslt = self.results[18]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
    #@unittest.skip('less verbose debug')
    def test_case_json_19j(self):
        args = self.params[19]
        rslt = self.results[19]
        ret = setPath(*args)
        self.assertEqual(ret, rslt)
#pylint: enable=attribute-defined-outside-init

if __name__ == '__main__':

    tests = unittest.TestLoader().loadTestsFromTestCase(TestCaseJson)
    result = unittest.TextTestRunner(verbosity=3).run(tests)
    status = 'OK' if result.wasSuccessful() else 'FAILED (failures = ' + \
                str(len(result.failures)) + ')\n' + 'ERRORS (errors   = ' + \
                str(len(result.errors)) + ')\n'
    print('\nRan {} tests \n\n{}' \
          .format(result.testsRun, status))
    if result.failures:
        print(('Fails:' + '\n {}'*len(result.failures)) \
              .format(*result.failures))
    if result.errors:
        print(('Errs:' +  '\n{}'*len(result.errors[0])) \
              .format(*result.errors[0]))
#pylint: enable=invalid-name
