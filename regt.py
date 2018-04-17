# -*- coding: utf-8 -*-
"""
.. created: on Thu Feb 22 16:24:45 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""
from version import __version__
import re
import os
import unittest
import logging

def SlashContrl(strpath):
    '''
       Solves windows - os.path normalize fail
       for i.e. tests\\tests, considers \t an escape sequence.

       :filters:: ['\\r', '\\t', '\\f', '\\a', '\\v'].

       :return: true path [str]

       *other specific escape chars not filtered*

    '''
    if not strpath or strpath == ' ':
        return None

    cntrls = ['r', 't', 'f', 'a', 'v']
    res = None
    dbblstr = None
    for  ct in cntrls:
        res = re.search('[\\' + ct + ']', strpath)
        if res:
            dbblstr = strpath[0:res.start()] + r'\\' + ct + strpath[res.end():]
            if not dbblstr:
                return None
            return os.path.normpath(os.path.abspath(dbblstr))
    return os.path.normpath(os.path.abspath(strpath))

#pylint: disable=attribute-defined-outside-init
#pylint: disable=invalid-name

#@unittest.skip("skipping TestCaseDoubleSlash")
class TestCaseDoubleSlash(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cwd = os.getcwd()
        cls.pardir = os.path.dirname(os.getcwd())
        tdir = '\\Tests'
        if 'Tests' in os.getcwd():
            logging.warn('\n pardir {}'.format(cls.pardir))

        cls.parStrs = {'0':'Tests\rtest.py',
                       '1': '..\\Tests\test.py',
                       '2': '.\\Tests/fest.py',
                       '3': '.\\tests\ttest.py'
                      }

        cls.resultStrs = {'0':os.path.join(cls.cwd + tdir + '\\rtest.py'),
                          '1':os.path.join(os.path.dirname(cls.cwd) + tdir + \
                                           '\\test.py'),
                          '2':os.path.join(cls.cwd + tdir + '\\fest.py'),
                          '3':os.path.join(cls.cwd + '\\tests\\ttest.py')
                         }
        #logging.warn('\n dict slsh 3 {}'.format(cls.resultStrs['3']))
        cls.cwd = os.getcwd()

        print("\n\t" +  cls.__name__ + "  set-up")
    @classmethod
    def tearDownClass(cls):
        print "\n" + cls.__name__ + " tear down"

    def setUp(self):
        print("\n" +  self.id() + "  Set-up")

    def tearDown(self):
        print "\n" + self.id() + " Tear down"

    def test_backslash_and_Controls_0(self):

        par = self.parStrs['0']
        ret = self.resultStrs['0']
        self.assertEqual(SlashContrl(par), ret)

    def test_backslash_and_Controls_1(self):

        par = self.parStrs['1']
        ret = self.resultStrs['1']
        self.assertEqual(SlashContrl(par), ret)

    def test_backslash_and_Controls_2(self):

        par = self.parStrs['2']
        ret = self.resultStrs['2']
        self.assertEqual(SlashContrl(par), ret)

    def test_backslash_and_Controls_3(self):

        par = self.parStrs['3']
        ret = self.resultStrs['3']
        self.assertEqual(SlashContrl(par), ret)

if __name__ == '__main__':

    tests = unittest.TestLoader().loadTestsFromTestCase(TestCaseDoubleSlash)
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

#pylint: enable=attribute-defined-outside-init
#pylint: enable=invalid-name
