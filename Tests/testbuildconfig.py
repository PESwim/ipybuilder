# -*- coding: utf-8 -*-
"""
.. created on Wed Feb 14 19:41:13 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

   If unittest is run *before* ipybuild you MUST restart
   the python interpreter to get logging in ipybuild runs.
     *make sure ipybuild ret after main is not assigned*  
   
   Too Complex unittest using subprocess to test realtime
   inputs (tests avoid final complie)
   
   
   The tests are created in a test factory loop to pick up
   MAINARGS and COMDARGS in testbuildargs.py
   
   Captured output results RESULTS are compared and created files
   are deleted after each test.
   
   Most difficult is the log capture which scrapes the written
   files log for deletion, but must be time based and is too sensetive 
   to intermediate function runtimes for stable results.
   
   *These tests passed on a Toshiba laptop running at 2.2GHz with
    an 64 bit Intel(R) Core(TM) i7-2670QM CPU/Windows 7 64 Python 2.7 (32bit)*
   
   TODO: MOCK to completly separate production from tests
         Imporve or Change log timing, scraping, deleteing
   *Run unittest with a new filelog*

"""
#pylint: disable=attribute-defined-outside-init
#pylint: disable=invalid-name
import sys
import os
import time
import logging
import unittest
import cStringIO

MUSTSKIP = ['Assign', 'Json', 'Slash']

if 'Tests' in os.getcwd():
    sys.path.append(os.path.join(os.pardir,
                                 os.path.dirname(os.getcwd())))
else:
    sys.path.append(os.path.join(os.getcwd()))

from makedefault import (maindict, defaultjson, defaultcfg,
                         defaultconfig, setPath, ndcDict,
                         assembly_json)

from partialerror import FatalError
from ipybuild import  CmdConfig as Build_Test
from ipybuild import  MainConfig as ScriptBuild_Test
from partialerror import PartialErrors
import filecontrol
from filecontrol import (checkRequired, setLogLookBackTimeSec,
                         getWriteLog, delTestFileWrites,
                         CompareFilesConfirmedToRequired,
                         getFilesWritten, getFilesConfirmed)

from testbuildargs import TESTCMDARGS, TESTMAINARGS
from buildlogs import terminalC
FORMTINFO = "%(levelname)-7.7s [%(funcName)s] %(message)s"

log = logging.getLogger(__name__)

if not log.handlers:
    lh = terminalC(sys.stdout)
    lf = logging.Formatter(fmt=FORMTINFO)
    lh.setFormatter(lf)
    log.addHandler(lh)
    log.setLevel(logging.INFO)
    log.propagate = False

def setUpModule():
    log.warn('\n log test should FILE - INFO-CRIT:\n')
    log.FILE('______________' + \
                     str(time.strftime('%x %X', time.localtime())) + \
                           '____________')
    log.FILE('\t UNITTEST')
    log.debug('\t')
    log.info('\t')
    log.fatal('\t')

def tearDownModule():
    pass

#@unittest.skip("showing class TestCaseUserCMD")
class TestCaseUserCMD(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('-'*59)
        cls.default = os.path.join(os.getcwd(), 'default_config.config')
        opj = os.path.join
        onp = os.path.normpath
        reqtestPath = onp(opj(os.path.abspath(opj(os.getcwd(),
                                                  os.pardir)),
                              'unittest.txt'))

        cls.tfiles = checkRequired(reqtestPath)
        
        # TODO set lookback by start-cur times
        cls.startTimeSecs = None
        cls.written = None
        print("\n\t" +  cls.__name__ + "  set-up")

    @classmethod
    def tearDownClass(cls):
        cls.tfiles = None
        print "\n\t" + cls.__name__ + " tear down"

    def qLog(self):
        print('\n startTime {}'.format(time.time()-self.startTimeSecs))

        setLogLookBackTimeSec(3)
        curDateTime = time.strftime('%x %X', time.localtime())
        lfiles = list(getWriteLog())
        cnffiles = None
        wfiles = None
        cmplst = None
        
        if lfiles:
            cnffiles = getFilesConfirmed(list(lfiles))
            wfiles = getFilesWritten(list(lfiles))
            
        if cnffiles and wfiles:
            cmplst = CompareFilesConfirmedToRequired(cnffiles, self.tfiles)
            if  cmplst:
                #log.error(('\n cmplst {}'*len(cmplst)).format(*cmplst))
                raise FatalError('ValueError',
                                 ('\n {}'*len(cmplst)).format(*cmplst))
            print('-'*59)
            print(('log read time{}\n' + \
                  'proc start time {}').format(curDateTime, self.startTime))

            print(('\n confirmed:' + '\n {}'*len(cnffiles)).format(*cnffiles))
            print('-'*59)
            print(('\n writtten:' + '\n {}'*len(wfiles)).format(*wfiles))
            
    def errTraceErr(self):

        errpos = self.err.find('Trace')
        if errpos == -1:
            errpos = self.err.find('Errno')#python base error
            errpos = 0 if errpos > 0 else len(self.err)
        self.err = '\t'+ self.err[errpos:]
        return ('\n\t').join(self.err.split('\r\n'))
    
    def delGeneratedFiles(self):
        setLogLookBackTimeSec(3)
        curDateTime = time.strftime('%x %X', time.localtime())

        written = None
        if self.written:
            written = list(self.written)

        delfiles = None
        if written:
            delfiles = delTestFileWrites(list(written))
            print('\n ****** deleted  ' + curDateTime + '  *******')
            print(('\n {}'*len(delfiles)).format(*delfiles))
        else:
            print('\n ****** NONE deleted  ' + curDateTime + '  CHECK *******')
            
    def setUp(self):
        print("\n\t" +  self.id() + " set-up self")
        self.cmd = Build_Test
        self.err = None
        self.startTime = None
        self.written = None
        
    def tearDown(self):
        self.err = None
        self.qLog()
        
#        todel = getFilesWritten(getWriteLog())
        todel = self.written
        if todel:
            print(('\n Should be deleted:\n' + '{}\n'*len(todel)) \
                  .format(*todel))
        else:
            print('\n Nothing in to delete')
            
        self.delGeneratedFiles()
        if todel:
            for f in todel:
                if not os.path.isdir(f):
                    msg = 'del failed with:\n{}'.format(f)
                    assert not os.path.exists(f), msg

        print("\n\t" +  self.id() + " tear-down self")

def createCMDtest(name, noskip, pairs):
    '''parameters scope through to test_CMD'''
    print('-'*59)
    if noskip:
        print('\n\t creating {} '.format(name))
        print(('\n testing Build:' + '\n\t{}'*len(pairs[1])).format(*pairs[1]))
    else:
        print(('\n\tskipped {}:\n\t Build:'+  \
               '\n\t {}'*len(pairs[1])).format(name, *pairs[1]))

    print('-'*59)
    if not noskip:
        return None

    def create_test_CMD(self):

        print(('set up Subprocess - checking for ' + \
              '"{}" in output').format(pairs[0]))
        skipWrite = False
        import subprocess
        from subprocess import PIPE
        self.po = subprocess.Popen
        time.sleep(3.5)
        self.startTimeSecs = time.time()
        self.startTime = time.strftime('%x %X', time.localtime())
        p = self.po(pairs[1], stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        if 'Trace' in stderr or 'Err' in stderr:
            self.err = stderr
            if pairs[0][0] == 'Error':
                skipWrite = True
                self.errTraceErr()
                log.error('\n{}'.format(self.err))
                self.assertTrue('Error' in self.err)
                print('tear down Subprocess')
                p.kill()
                #print('*'*59)
                #log.warn(('\n stdout ' + '*'*50 + '\n{}'*len(stdout.split('\n')) + '\nend' +'*'*59) \
                # .format(*stdout.split('\n')))
                #print('*'*59)
                return True
            # un-expected err
            elif self.errTraceErr():
                log.error('\n unexpected err\n: {}'.format(self.errTraceErr()))

        p.kill()

        # debug unittest
        #print('*'*59)
        #log.warn(('\n stdout ' + '*'*50 + '\n{}'*len(stdout.split('\n')) + '\nend' +'*'*59) \
        #         .format(*stdout.split('\n')))
        #print('*'*59)

        if not skipWrite:
            curDateTime = time.strftime('%x %X', time.localtime())
            setLogLookBackTimeSec(3)
            writes = getFilesWritten(list(filecontrol.getWriteLog()))

            if writes:
                self.written = list(writes)
                self.assertTrue(len(writes)>0)

            m = []
            for fl in pairs[2]:
                m.extend([wrt for wrt in writes if fl.strip() in wrt])
                
            #don't know when program will exit depends on err
            if 'Error' not in pairs[0]:
                self.assertTrue(len(m) > 0)
                self.assertEqual(len(pairs[2]), len(m))
            print('passed look back 3 sec at {}'.format(curDateTime))

        self.assertTrue(pairs[0][0] in stdout)
        self.assertTrue(pairs[0][1] in stdout)

    return create_test_CMD

#@unittest.skip("showing class TestCaseUserMAIN")
class TestCaseUserMAIN(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('-'*59)
        cls.stdout_ = sys.stdout
        cls.default = os.path.join(os.getcwd(), 'default_config.config')
        opj = os.path.join
        opn = os.path.normpath
        reqtestPath = opn(opj(os.path.abspath(opj(os.getcwd(),
                                                  os.pardir)),
                              'unittest.txt'))

        cls.tfiles = checkRequired(reqtestPath)
        cls.startTimeSecs = None
        cls.written = None
        print("\n\t" +  cls.__name__ + "  set-up")

    @classmethod
    def tearDownClass(cls):
        print "\n\t" + cls.__name__ + " tear down"

    def qLog(self):
        
        setLogLookBackTimeSec(3)
        curDateTime = time.strftime('%x %X', time.localtime())
        lfiles = list(getWriteLog())
        cnffiles = None
        wfiles = None
        cmplst = None

        if lfiles:
            cnffiles = getFilesConfirmed(list(lfiles))
            wfiles = getFilesWritten(list(lfiles))

        if cnffiles and wfiles:
            cmplst = CompareFilesConfirmedToRequired(cnffiles, self.tfiles)
            if  cmplst:
                raise FatalError('ValueError',
                                 '\n {}'*len(cmplst).format(*cmplst))
            print('-'*59)
            print(('log read time{}\n' + \
                  'proc start time {}').format(curDateTime, self.startTime))

            print(('\n confirmed:' + '\n {}'*len(cnffiles)).format(*cnffiles))
            print('-'*59)
            print(('\n writtten:' + '\n {}'*len(wfiles)).format(*wfiles))
    
    def delGeneratedFiles(self):
        setLogLookBackTimeSec(3)
        curDateTime = time.strftime('%x %X', time.localtime())

        written = None
        if self.written:
            written = list(self.written)

        delfiles = None
        if written:
            delfiles = delTestFileWrites(list(written))
            print('\n ****** deleted  ' + curDateTime + '  *******')
            print(('\n {}'*len(delfiles)).format(*delfiles))
        else:
            print('\n ****** NONE deleted  ' + curDateTime + '  CHECK *******')
    
    def cap(self):
        self.capturedOutput.truncate(0)
        self.capturedOutput.seek(0)
        sys.stdout = self.capturedOutput

    def uncap(self):
        sys.stdout = self.stdout_

    def setUp(self):

        self.main = ScriptBuild_Test
        self.startTime = None
        
        try:
            self.capturedOutput = cStringIO.StringIO()
        except NameError as ex:
            print(type(ex))
            sys.stdout = self.stdout_
        print("\n\t" +  self.id() + " set-up self")

    def tearDown(self):
        sys.stdout = self.stdout_
        self.capturedOutput.close()
        self.qLog()
        todel = getFilesWritten(getWriteLog())
        if todel:
            print(('\n Should be deleted:\n' + '{}\n'*len(todel)) \
                  .format(*todel))
        else:
            print('\n Nothing in to delete')
        
        self.delGeneratedFiles()
        if todel:
            for f in todel:
                if not os.path.isdir(f):
                    msg = 'del failed with:\n{}'.format(f)
                    assert not os.path.exists(f), msg
        print("\n\t" +  self.id() + " tear-down self")

def createMAINtest(name, noskip, pair):
    '''parameters scope through to test_MAIN'''

    print('-'*59)
    if noskip:
        print('\n\t creating {} '.format(name))
        print(('\n testing ScriptBuild:' + '\n\t{}'*len(pair[1])) \
              .format(*pair[1]))
    else:
        print(('\n\tskipped {}:\n\t ScriptBuild:'+  \
               '\n\t {}'*len(pair[1])).format(name, *pair[1]))

    print('-'*59)

    if not noskip:
        return None

    def create_test_MAIN(self):

        print(('ScriptBuild run - checking for ' + \
              '"{}" in output').format(pair[0]))
        skipWrite = False
        if pair[0][0] == 'Error':
            skipWrite = True
            setLogLookBackTimeSec(3)
            lfiles = list(getWriteLog())
            writes = getFilesWritten(list(lfiles))
            self.written = writes
            self.startTimeSecs = time.time()
            return True
        
        time.sleep(3.5)
        self.startTimeSecs = time.time()
        self.startTime = time.strftime('%x %X', time.localtime())
        self.cap()
        self.main(*pair[1])
        self.uncap()
        print('tear down capture')

        # debug unittest
        #print('*'*59)
        #log.info('\ncap:\n\t {}'.format(self.capturedOutput.getvalue()))
        #print('*'*59)

        lfiles = None

        if not skipWrite:
            curDateTime = time.strftime('%x %X', time.localtime())
            setLogLookBackTimeSec(3)
            lfiles = list(getWriteLog())
            writes = getFilesWritten(list(lfiles))

            self.written = writes
            if writes:
                self.assertTrue(len(writes)>0)

            m = []
            for fl in pair[2]:
                m.extend([wrt for wrt in writes if fl.strip() in wrt])
                
            # don't know when program will exit depends on err
            if 'Error' not in pair[0]:
                self.assertTrue(len(m) > 0)
                self.assertEqual(len(pair[2]), len(m))
            print('passed look back 3 sec at {}'.format(curDateTime))

        self.assertTrue(pair[0][0] in self.capturedOutput.getvalue())
        self.assertTrue(pair[0][1] in self.capturedOutput.getvalue())

    return create_test_MAIN

COMMANDS = TESTCMDARGS

MAINARGS = TESTMAINARGS
# carefull with escape chars \a \n etc.   use \\
#CMDARGS
RESULTS = [('*ERR -0', 'Tests\make.dll'),
           ('Error', ''),
           ('*ERR -0', 'Tests\\appname.exe'),
           ('Tests\make.dll', '*ERR -1'),
           ('Re-run ipybuilder', '*ERR -0'),
           ('OK - Building file', '*ERR -0 '),
           ('Build state OK', 'Build state OK')
          ]
#MAINARGS
RESULTS_ = [('*Re-run ipybuilder', '*ERR -0'),
            ('Error', ''),
            ('*Re-run ipybuilder', '*ERR -0'),
            ('*Re-run ipybuilder', '*ERR -0'),
            ('*Re-run ipybuilder', '*ERR -0'),
            ('*Re-run ipybuilder', '*ERR -0'),
            ('*Re-run ipybuilder', '*ERR -0')
           ]

opn = os.path.normpath
WRITES = [[opn(os.getcwd() + '\UserDefaulted\make_assembly_config.config'),
           opn(os.getcwd() + '\\release\\make.zip')],

          [opn(os.getcwd() + '\UserDefaulted\maketest_config.config'),
           opn(os.getcwd() + '\\release\\make.zip')],

          [opn(os.getcwd() + '\\appname_config.config'),
           opn(os.getcwd() + '\\release\\appname.zip')],

          [opn(os.getcwd() + '\\maketest_config.config'),
           opn(os.getcwd() + '\\release\\make.zip')],

          [opn(os.getcwd() + '\\make_test_config.config'),
           opn(os.getcwd() + '\\release\\make_test.zip')],

          [opn(os.getcwd() + '\\UserDefaulted\default_config.config')],

          [opn(os.getcwd() + '\\UserDefaulted\\default_config.config')]
         ]

log.debug('\n name {} CWD: {}'.format(__name__, os.getcwd()))

if 'Tests' in os.getcwd():
    for i, pair in enumerate(COMMANDS):
        txt = 'test_Build_'+ str(i)
        test_method = createCMDtest(txt, pair[1], (RESULTS[i],
                                     pair[0], WRITES[i]))
        if pair[1]:#no-skip
            test_method.__name__ = txt
            setattr(TestCaseUserCMD, test_method.__name__, test_method)

    for i, mpair in enumerate(MAINARGS):
        txt = 'test_ScriptBuild_'+ str(i)
        test_method = createMAINtest(txt, mpair[1], (RESULTS_[i],
                                                     mpair[0], WRITES[i]))
        if mpair[1]:#no-skip
            test_method.__name__ = txt
            setattr(TestCaseUserMAIN, test_method.__name__, test_method)

def _gen_testnames(modname):

    names = []
    for testcls in [t for t in dir(sys.modules[modname]) \
                if 'TestCase' in t and t != 'TestCase' and \
                 all(mk not in t for mk in MUSTSKIP)]:
        for tcase in dir(getattr(sys.modules[modname], testcls)):
            if 'test' in tcase and not 'config' in tcase:
                names.append(modname + '.' + testcls + '.' + tcase)
   
    return names

def gen_failReport(report_):

    fails = []
    for fail in report_.failures:
        args = []
        for arg in fail:
            args.append(str(arg))
        fails.append(args)
        print(report_.separator1)
        for k, ln in enumerate(fails[-1]):
            if k == 1:
                print(report_.separator1)
            if k == 0:
                print('FAIL: ' + ln)
            else:
                print(ln)
        print(report_.separator2)

def gen_errorReport(report_):

    errs = []
    for err in report_.errors:
        args = []
        for arg in err:
            args.append(str(arg))
        errs.append(args)
        print(report_.separator1)
        for k, ln in enumerate(errs[-1]):
            if k == 1:
                print(report_.separator1)
            if k == 0:
                print('ERROR: ' + ln)
            else:
                print(ln)
        print(report_.separator2)

def runtest(module_name=__name__, verbosity=0):

    names = _gen_testnames(module_name)
    tests = unittest.defaultTestLoader.loadTestsFromNames(names)
    #OKprint(('\n').join([str(s) for s in tests._tests]))
    # -- this way avoids internal runner Result output
    suite = unittest.TestSuite(tests)
    report = unittest.TestResult()
    report.separator0 = u'\u203E'*59
    report.separator1 = '_'*59
    report.separator2 = '-'*59
    ts = time.time()
    suite.run(report)
    # this -- way is fine if standard output wanted
    #    runner = unittest.TextTestRunner(verbosity=verbosity)
    #    report = runner.run(tests)

    tt = time.time()-ts

    if report.errors:
        gen_errorReport(report)
    if report.failures:
        gen_failReport(report)

    status = 'OK' if report.wasSuccessful() else 'FAILED (failures = ' + \
                str(len(report.failures)) + ')\n' + 'ERRORS (errors   = ' + \
                str(len(report.errors)) + ')\n'
    addedSleepTime = round(tt-.8)
    print(('\nRan {} tests in {:4.3f} secs\n\t' + \
          '* with readwrite sleep ~{} sec\n\n{}') \
          .format(report.testsRun, tt, addedSleepTime, status))

    curDateTime = time.strftime('%x %X', time.localtime())
    log.info('time {}'.format(curDateTime))

#pylint: enable=attribute-defined-outside-init

if __name__ == '__main__':
    runtest(__name__, verbosity=3)
#pylint: enable=invalid-name
