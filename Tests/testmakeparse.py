# -*- coding: utf-8 -*-
"""
.. created on Wed Feb 14 19:41:13 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""
#pylint: disable=attribute-defined-outside-init
#pylint: disable=invalid-name
import sys
import os
from os.path import isfile as opi
from os.path import abspath as opabs
import json
import unittest
from collections import OrderedDict

if 'Tests' in os.getcwd():
    sys.path.append(os.path.join(os.pardir, os.path.dirname(os.getcwd())))

else:
    sys.path.append(os.path.join(os.getcwd()))

import makedefault
from makedefault import maindict, defaultcfg, ndcDict
from makeload import LoadConfig
from partialerror import PartialErrors
from ipybuild import CmdConfig
from ipybuild import MainConfig
from buildlogs import dynfile

log = dynfile(__name__)

#@unittest.skip("showing class TestCaseArgsAssign")
class TestCaseArgsAssign(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('-'*59)
        log.info('\n defaultcfg {} '.format(defaultcfg))
        cls.defaultcfg = os.path.normpath(defaultcfg.replace('\\Tests', ''))
        log.info('\n cls.defaultcfg {} '.format(cls.defaultcfg))
        cls.maindict = OrderedDict(maindict)
        cls.parErr = PartialErrors
        assert cls.maindict == maindict, 'different dicts'

        cls.argslst = [('mock/locate_listexe.txt'),
                       ('mock/locate_listexe.txt', 'mock/locate_listdll.txt'),
                       ('mock/locate_listexe.txt', None, 
                        'mock\\inst\\zip\\ziplist.txt')]
                       
        cls.kwargslst = {'listexe' : 'mock/locate_list.txt',
                         'listzip' : 'mock\\zip_locate.txt',
                         'json'    : 'Tests\\assembly.json'}
        # result Main args
        cls.mainArg = OrderedDict([('configPath', ' '),
                                   ('mainName', 'mock\\appname.py'),
                                   ('outDir', '.\\release'),
                                   ('makeEXE', False)])
        # result Cmd args 
        cls.argDict = OrderedDict([('configPath', ' '),
                                   ('mainName', 'mock\\appname.py'),
                                   ('outDir', '.\\release'),
                                   ('json', None),
                                   ('makeEXE', False),
                                   ('listexe', None),
                                   ('listdll', None),
                                   ('listzip', None)])

        cls.argDict1 = ndcDict(cls.argDict)
        cls.argDict1['listexe'] = 'mock/locate_listexe.txt'

        cls.argDict2 = ndcDict(cls.argDict1)
        cls.argDict2['listdll'] = 'mock/locate_listdll.txt' #Adding

        cls.argDict3 = ndcDict(cls.argDict1)
        cls.argDict3['listzip'] = 'mock\zip_locate.txt'#Changing
        cls.argDict3['json'] = 'Tests\assembly.json'

        cls.argDict4 = OrderedDict([('configPath', ' '),
                                    ('mainName', 'mock\make.py'),
                                    ('outDir', None),
                                    ('json', None),
                                    ('makeEXE', False),
                                    ('listexe', None),
                                    ('listdll', None),
                                    ('listzip', None)])

        #log.debug('\n *argDict chk typ {} dict{}'.format(type(cls.argDict), \
        #                                                   str(cls.argDict)))

        cls.argDicts = [cls.argDict, cls.argDict1, cls.argDict2,
                        cls.argDict3, cls.argDict4
                       ]
        #cmdline args
        cls.sysargv_lst = [([__name__, None, 'mock\\appname.py', '.\\release'],
                            cls.argDicts[0]),
                           ([__name__, None, 'mock\\appname.py', '.\\release',
                             None, cls.argslst[0]],
                            cls.argDicts[1]),
                           ([__name__, None, 'mock\\appname.py', '.\\release',
                             None, cls.argslst[1]],
                            cls.argDicts[2]),
                           ([__name__, None, 'mock\\appname.py', '.\\release',
                             None, cls.kwargslst],
                            cls.argDicts[3]),
                           ([__name__, None, 'mock\\make.py'],
                            cls.argDicts[4])]

        for par in cls.sysargv_lst:
            #log.debug('\n par[1] type{}'.format(type(par[1])))
            assert isinstance(par[1], OrderedDict), \
                            'Error in unittest cls setUp'
            assert cls.maindict.keys() == par[1].keys(), \
                            'cls ordereddict not eqaual'

        print("\n\t" +  cls.__name__ + "  set-up")
        print('-'*59)

    def errTraceErr(self):

        errpos = self.err.find('Trace')
        if errpos == -1:
            errpos = self.err.find('Errno')#python base error
            errpos = 0 if errpos > 0 else len(self.err)

        self.err = '\t'+ self.err[errpos:]

        return ('\n\t').join(self.err.split('\r\n'))

    def setUp(self):

        print("\n\t" +  self.id() + " set-up self")
        self.parErr = []
        self.main = MainConfig
        self.cmd = CmdConfig
        self.err = None
        self.syslist = []
        self.outdict = []

        for params in self.sysargv_lst:

            self.syslist.append(params[0])
            paramdict = OrderedDict(self.maindict)
            paramdict.update(params[1])
            self.outdict.append(paramdict)
            
    def tearDown(self):
        print("\n\t" +  self.id() + " tear-down self")
        self.syslist = None
        self.sysargv = None
        self.mainargs_out = None
        self.outdict = None
        
    def runTest(self):
        pass
    #@unittest.skip("test_comman_shows_help")
    def test_comman_shows_help(self):

        print('set up Subprocess - checking for ' + \
              '"Example" in help txt')
        import subprocess
        from subprocess import PIPE
        self.po = subprocess.Popen
        if 'Tests' in os.getcwd():
            p = self.po(['python', '..\ipybuild.py', '/h'], \
                        stdout=PIPE, stderr=PIPE)

        else:
            p = self.po(['python', 'ipybuild.py', '/h'], \
                        stdout=PIPE, stderr=PIPE)

        stdout, stderr = p.communicate()

        #print('*************************\n' + str(stdout))
        if 'Trace' in stderr or 'Err' in stderr:
            self.err = stderr
            log.error('\n{}'.format(self.errTraceErr()))
            print('tear down Subprocess')

        p.kill()

        self.assertTrue('Example' in stdout)
        self.assertEqual(0,len(PartialErrors))
    #@unittest.skip("test_Catch_python_make_errs_from_subproc")
    def test_Catch_python_make_errs_from_subproc(self):

        print('set up Subprocess')
        import subprocess
        from subprocess import PIPE
        self.po = subprocess.Popen

        p = self.po(['python', 'ipybuild', 'mock try', 'mock arg'],
                    stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        if 'Trace' in stderr or 'Err' in stderr:
            self.err = stderr
            log.info('\n{}\n{}'.format('TEST IS PASSING ON MOCK ERROR:' +\
                                       ' to show debug use',
                                       self.errTraceErr()))
            print('tear down Subprocess')
        p.kill()

        self.assertFalse(p.returncode == 0)
        self.assertEqual(0,len(PartialErrors))
        
    #unittest.skip("test_default_userconfig_atleast")
    def test_default_userconfig_atleast(self):
        if 'Test' in os.getcwd():
            self.assertEqual(self.defaultcfg,
                             os.path \
                             .abspath(os.path \
                             .join(os.getcwd(), '..',
                                   'defaults',
                                   'default_config.config')))
        else:
            self.assertEqual(defaultcfg,
                             os.path.join(os.getcwd(),
                                          'defaults',
                                          'default_config.config'))

        with open(self.defaultcfg, 'r') as  cr:
            testdefault = json.load(cr)

        self.assertNotEqual(testdefault, None)
        self.assertEqual(0,len(PartialErrors))
        
    #@unittest.skip("test_command_first3_assigned_0")
    def test_command_first3_assigned_0(self):

        self.mainargs_out = self.outdict[0]
        self.sysargv = self.syslist[0]
        
        # keep for debug
        #log.warn('\nself.mainargs_out \n\t{}'\
        #          .format(json.dumps(self.mainargs_out, indent=4)))
        #log.warn('\nself.sysargv \n\t{}'\
        #          .format(str(self.sysargv)))
        #log.warn('\nself.result \n\t{}'\
        #          .format(json.dumps(self.cmd(self.sysargv), indent=4)))

        self.assertEquals(self.cmd(self.sysargv), self.mainargs_out)
        self.assertEqual(0,len(PartialErrors))
        
    #@unittest.skip("test_main_first3_assigned_0")
    def test_main_first3_assigned_0(self):

        self.mainargs_out = OrderedDict(self.outdict[0])
        self.args = tuple(self.syslist[0][1:])
        
        # keep for debug
        #log.warn('\nself.mainargs_out \n\t{}'\
        #          .format(json.dumps(self.mainargs_out, indent=4)))
        #log.warn('\nself.args \n\t{}'\
        #          .format(str(self.args)))
        #log.warn('\nself.result \n\t{}'\
        #          .format(json.dumps(self.main(*self.args), indent=4)))
        self.assertEquals(self.main(*self.args), self.mainargs_out)
        self.assertEqual(0,len(PartialErrors))
    #@unittest.skip("test_command_first3_assigned_1")
    def test_command_first3_assigned_1(self):

        self.mainargs_out = self.outdict[1]
        self.sysargv = self.syslist[1]
        self.assertEquals(self.cmd(self.sysargv), self.mainargs_out)
        self.assertEqual(0,len(PartialErrors))
        
    #@unittest.skip("test_main_first3_assigned_1")
    def test_main_first3_assigned_1(self):
        self.mainargs_out = self.outdict[1]
        self.args = tuple(self.syslist[1][1:])#[1:] filtered
        self.assertEquals(self.main(*self.args), self.mainargs_out)
        self.assertEqual(0,len(PartialErrors))
    #@unittest.skip("test_command_first3_assigned_2")
    def test_command_first3_assigned_2(self):
        self.mainargs_out = self.outdict[2]
        self.sysargv = self.syslist[2]
        self.assertEquals(self.cmd(self.sysargv), self.mainargs_out)
        self.assertEqual(0,len(PartialErrors))
    #@unittest.skip("test_main_first3_assigned_2")
    def test_main_first3_assigned_2(self):

        self.mainargs_out = self.outdict[2]
        self.args = tuple(self.syslist[2][1:])
        self.assertEquals(self.main(*self.args), self.mainargs_out)
        self.assertEqual(0,len(PartialErrors))
    #@unittest.skip("test_command_first3_assigned_3")
    def test_command_first3_assigned_3(self):

        self.mainargs_out = self.outdict[2]
        self.sysargv = self.syslist[2]
        self.assertEquals(self.cmd(self.sysargv), self.mainargs_out)
        self.assertEqual(0,len(PartialErrors))
        
    #@unittest.skip("test_main_first3_assigned_3")
    def test_main_first3_assigned_3(self):

        self.mainargs_out = self.outdict[2]
        self.args = tuple(self.syslist[2][1:])
        self.assertEquals(self.main(*self.args), self.mainargs_out)
        self.assertEqual(0,len(PartialErrors))
    
    #@unittest.skip("test_command_first3_assigned_4")
    def test_command_first3_assigned_4(self):

        self.mainargs_out = self.outdict[2]
        self.sysargv = self.syslist[2]
        self.assertEquals(self.cmd(self.sysargv), self.mainargs_out)
        self.assertEqual(0,len(PartialErrors))
   
    #@unittest.skip("test_main_first3_assigned_4")
    def test_main_first3_assigned_4(self):

        self.mainargs_out = self.outdict[2]
        self.args = tuple(self.syslist[2][1:])
        self.assertEquals(self.main(*self.args), self.mainargs_out)
        self.assertEqual(0,len(PartialErrors))
    
    @classmethod
    def delTearDownClass(cls):
        if 'Tests' in os.getcwd():
            print('del {}'.format('mock\appname_assembly.json'))    
            try:
                os.remove(opabs('mock\\appname_assembly.json'))
            except WindowsError:
                pass
        
        if 'Tests' in os.getcwd():
            print('del {}'.format('mock\appname_config.config'))
            try:
                os.remove('mock\\appname_config.config')
            except WindowsError:
                pass
    
    @classmethod
    def tearDownClass(cls):
        cls.delTearDownClass()
        print("\n\t" +  cls.__name__ + " tear-down")
        cls.maindict = None
############################################################################

@unittest.skip("showing class TestCaseConfigAssign")
class TestCaseConfigAssign(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cwd = os.getcwd()
        cls.TESTCONFIG = os.getcwd() + '\mock\maketest_config.config'

        cls.maindict = maindict
        cls.defaultcfg = defaultcfg
        with open(cls.defaultcfg, 'r') as jr:
            cls.defconfig = json.load(jr)

        cls.mktestconfig = cls.TESTCONFIG

        print("\n\t" +  cls.__name__ + "  set-up")

    @classmethod
    def delTearDownClass(cls):
        print('cwd ', os.getcwd())
        if 'Tests' in os.getcwd():
            print('del {}'.format('mock\appname_assembly.json'))    
            try:
                os.remove(opabs('mock\appname_assembly.json'))
            except WindowsError:
                pass
        if 'Tests' in os.getcwd():
            print('del {}'.format('mock\appname_config.config'))    
            try:
                os.remove(opabs('mock\appname_config.config'))
            except WindowsError:
                pass
            
    @classmethod
    def tearDownClass(cls):
        print("\n\t" +  cls.__name__ + " tear-down")
        cls.maindict = None
        if os.path.isfile(cls.mktestconfig):
            os.remove(cls.mktestconfig)
        cls.delTearDownClass()
        
    def runTest(self):
        pass
    def setUp(self):

        with open(defaultcfg, 'r') as jdcr:
            self.defcon = json.load(jdcr)
        assert self.defcon
        self.loadconfig = LoadConfig
        self.main = MainConfig
        self.cmd = CmdConfig
        self.maxDiff = None
        unittest.util._MAX_LENGTH = 2000
        print("\n\t" +  self.id() + " set-up self")

    def tearDown(self):
        print("\n\t" +  self.id() + " tear-down self")

    def FullDictCheck(self, rslt, target):
        # full dict check
        dicmp = []
        for k in rslt.keys():
            dicmp.append([k, [kr for kr in target.keys() if kr == k][0]])
            dic0 = []
            if isinstance(rslt[k], dict):
                dic1 = []
                for ky in rslt[k].keys():
                    dic1.append([ky, [kyr for kyr in target[k].keys() \
                                     if kyr == ky][0]])
                    dic2 = []
                    if isinstance(rslt[k][ky], dict):
                        for kys in rslt[k][ky].keys():
                            dic2.append([[kys, \
                                          [kysr \
                                           for kysr in target[k][ky].keys() \
                                           if kysr == kys][0]], \
                            rslt[k][ky][kys], target[k][ky][kys]])
                    else:
                        dic1.append([rslt[k][ky], target[k][ky]])
                    if dic2:
                        dic1.extend(dic2)
                if dic1:
                    dic0.extend(dic1)

            elif isinstance(rslt[k], (str, unicode)):
                dicmp.append([rslt[k], target[k]])
            if dic0:
                dicmp.extend(dic0)

        for dic in dicmp:
            if  isinstance(dic[0], list):
                for t in list(zip([v.replace('\\\\', '\\') for v in dic[0]],
                                  [w.replace('\\\\', '\\') for w in dic[1]])):
                    try:
                        self.assertEqual(t[0], t[1])
                    except AssertionError as ex:
                        log.warn('\nresults {}\ntargets {}'.format(*t))
                        raise ex
            else:
                try:
                    self.assertEqual(dic[0], dic[1])
                except AssertionError as ex:
                    log.warn('\nresults {dicr:}\ntarget {dictr:}' \
                             .format(dicr=dic[0], dictr=dic[1]))

    @unittest.skip('less verbose debug')
    def test_main_bad_configs_one_main(self):
        args = 'make.py'
        parsed = self.main(args)#no * for one arg
        self.ret = {u'MAINFILE': u'make.py',
                    u'ASSEMBLY': {u'product_version': u'0.0.0.1 alpha',
                                  u'copyright': u'Copyright 2018 - ' + \
                                  u'Howard Dunn. Apache 2.0 v2 Licensed.',
                                  u'company': u'Process Engineering LLC (PE LLC)',
                                  u'file_version': u'0.0.0.1',
                                  u'main': u'locate.py',
                                  u'product_name': u'PESwim installer',
                                  u'out': u'locater'},
                    u'CONFIGPATH': os.getcwd() + '\\make_config.config',
                    u'ZIPPATH': os.getcwd() + '\\make.zip',
                    u'JSONPATH': os.getcwd() + '\\make_assembly.json',

                    u'LISTFILES':{u'exe':
                                  [self.cwd + '\\assembly.json',
                                   self.cwd + '\\build.py',
                                   self.cwd + '\\__init__.py',
                                   self.cwd + '\\defaults\\assembly.json'],
                                  u'zip': [os.getcwd() +
                                           '\\mock\inst\\zip_list.txt'],
                                  u'dll': os.getcwd() + \
                                          '\\mock\inst\\locate_listdll.txt'},
                    u'MAKEDIR': u'' + os.getcwd(),
                    u'MAKEEXE': False,
                    u'OUTDIR': os.getcwd()
                   }

        self.result = self.loadconfig(parsed)
        self.assertTrue(all(k in self.result.keys() for k in self.ret.keys()))
        self.FullDictCheck(self.result, self.ret)
        self.assertEqual(0,len(PartialErrors))
    @unittest.skip('less verbose debug')
    def test_main_paritial_configs(self):
        args = self.mktestconfig, 'mock\\make.py'
        parsed = self.main(*args)
        config = self.loadconfig(parsed)
        self.assertEqual(config['MAINFILE'], os.getcwd()+'\\mock\\make.py')

    @unittest.skip('less verbose debug')
    def test_main_dll_config(self):

        if 'Tests' in os.getcwd():
            listfile = 'mock\inst\listdll.txt'
        else:
            listfile = 'Tests\mock\inst\listdll.txt'

        parsed = self.main(self.mktestconfig, 'mock\\make.py',
                           None, None, None, (listfile))

        config = self.loadconfig(parsed)
        self.assertEquals(len(config['LISTFILES']['dll']), 3)

    @unittest.skip('less verbose debug')
    def test_cmd_dll_config(self):

        if 'Tests' in os.getcwd():
            listfile = 'mock\inst\listdll.txt'
        else:
            listfile = 'Tests\mock\inst\listdll.txt'

        parsed = self.cmd([__name__, self.mktestconfig, 'mock\make.py',
                           None, None, None, (listfile)])
        config = self.loadconfig(parsed)
        self.assertEquals(len(config['LISTFILES']['dll']), 3)

#pylint: enable=attribute-defined-outside-init
#pylint: enable=invalid-name
if __name__ == '__main__':

    tests = unittest.TestLoader() \
                   .loadTestsFromTestCase(TestCaseArgsAssign)
    tests.addTests(unittest.TestLoader() \
                   .loadTestsFromTestCase(TestCaseConfigAssign))
    tests.addTests(unittest.TestLoader() \
                   .loadTestsFromTestCase(makedefault.TestCaseJson))
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
