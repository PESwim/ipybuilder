# -*- coding: utf-8 -*-
"""
.. created on Sat Apr 07 00:44:28 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

   Use with explorlib.py - see explorlib doc.

"""
import os
import sys
from version import __version__

# don't import on Shpinx Build
on_sphnx = False
try:
    os.environ.get('SPHINXBUILD')
    on_sphnx = True
except Exception as exs:
    pass
    
clr = None
try:
    import clr
except ImportError as ex:
    pass

if clr:
    try:
        clr.AddReference("System")
        import System
        clr.AddReference("StdLib")
    except System.IO.IOException as exc:
        print 'Failed StdLib AddRef - OK if standalone'
        print(exc)
    try:
        clr.AddReference("IronPython")
        import IronPython # checktoo see if used in exe version internally
    except System.IO.IOException as exc:
        print 'Fail to clr AddRef(s)'
        print(exc)
        
print 'libimport'
#pylint: disable=bad-continuation
# ---  trying direct ----
if not on_sphnx:
    import io
    import inspect
    import json
    import logging
    import re
    import os
    import subprocess
    import threading
    import traceback
    import zipfile
    import glob
    import locale
    import unittest
    import ctypes
    import ast
    import copy
    import xml
    
    import BaseHTTPServer
    import Bastion
    import CGIHTTPServer
    import ConfigParser
    import Cookie
    import DocXMLRPCServer
    import HTMLParser
    
    import shlex
    import md5
    import cmd
    import commands
    import binhex
    import numbers
    import pickle
    import user
    import sha
    import xmllib
    import argparse
    import chunk
    import Queue
    if clr:
        try: # (do not need if you know - not sure which lib reuqies)
            clr.AddReference("IronPython.SQLite")
        except System.IO.IOException as exc:
            print('"IronPython.SQLite" not availible as AddReference') # reminds you
    try:
        import UserList
        import UserString
        import aifc
        import anydbm
        import asynchat
        import asyncore
        import audiodev
        import bdb
        import bisect
        import calendar
        import cgitb
        import code
        import codeop
        import colorsys
        import compileall
        import cookielib
        import csv
        import decimal
        import dircache
        import distutils
        import doctest
        import dumbdbm
        import dummy_thread
        import dummy_threading
        import email
        import ensurepip
        import filecmp
        import fileinput
        import formatter
        import fpformat
        import fractions
        import ftplib
        import getopt
        import getpass
        import hmac
        import htmlentitydefs
        import htmllib
        import ihooks
        import imaplib
        import imghdr
        import importlib
        import imputil
        import lib2to3
        import macpath
        import macurl2path
        import mailbox
        import mailcap
        import mhlib
        import mimify
        import modulefinder
        import multifile
        import multiprocessing
        import mutex
        import netrc
        import new
        import nntplib
        import optparse
        import os2emxpath
        import pdb
        import pickletools
        import pipes
        import platform
        import plistlib
        import popen2
        import poplib
        import posixfile
        import profile
        import pstats
        import py_compile
        import pyclbr
        import pydoc_data
        import quopri
        import rexec
        import rlcompleter
        import robotparser
        import runpy
        import sched
        import sets
        import sgmllib
        import sha
        import shelve
        import smtpd
        import smtplib
        import sndhdr
        import sqlite3
        import sre_compile
        import sre_constants
        import sre_parse
        import statvfs
        import stringold
        import stringprep
        import sunau
        import sunaudio
        import symbol
        import tabnanny
        import tarfile
        import telnetlib
        import this
        import timeit
        import toaiff
        import trace
        import urllib2
        import uu
        import uuid
        import wave
        import webbrowser
        import whichdb
        import wsgiref
        import xdrlib
        
    except Exception as ex:
        print 'trucncated err msg'
        print(str(ex)[:255])

def Passed():
    '''
      *ALL THAT PASSED*

    '''
    passed = [
                'BaseHTTPServer',
                'Bastion',
                'CGIHTTPServer',
                'ConfigParser',
                'Cookie',
                'DocXMLRPCServer',
                'HTMLParser',
                'IronPython',
                'Queue',
                'SimpleHTTPServer',
                'SimpleXMLRPCServer',
                'SocketServer',
                'StringIO',
                'System',
                'UserDict',
                'UserList',
                'UserString',
                '_LWPCookieJar',
                '_MozillaCookieJar',
                '__builtin__',
                '__future__',
                '__main__',
                '_abcoll',
                '_ast',
                '_bisect',
                '_codecs',
                '_collections',
                '_csv',
                '_ctypes',
                '_dummy__threading_local',
                '_dummy_threading',
                '_functools',
                '_heapq',
                '_io',
                '_locale',
                '_md5',
                '_random',
                '_sha',
                '_sha256',
                '_sha512',
                '_ssl',
                '_struct',
                '_subprocess',
                '_warnings',
                '_weakref',
                '_weakrefset',
                '_winreg',
                'abc',
                'aifc',
                'anydbm',
                'argparse',
                'array',
                'ast',
                'asynchat',
                'asyncore',
                'atexit',
                'audiodev',
                'base64',
                'bdb',
                'binascii',
                'binhex',
                'bisect',
                'cPickle',
                'cStringIO',
                'calendar',
                'cgi',
                'cgitb',
                'chunk',
                'clr',
                'cmd',
                'code',
                'codecs',
                'codeop',
                'collections',
                'colorsys',
                'commands',
                'compileall',
                'contextlib',
                'cookielib',
                'copy',
                'copy_reg',
                'csv',
                'ctypes',
                'ctypes._ctypes',
                'ctypes._endian',
                'ctypes.ctypes',
                'ctypes.os',
                'ctypes.struct',
                'ctypes.sys',
                'datetime',
                'decimal',
                'difflib',
                'dircache',
                'dis',
                'distutils',
                'distutils.sys',
                'doctest',
                'dumbdbm',
                'dummy_thread',
                'dummy_threading',
                'email',
                'email.Charset',
                'email.Encoders',
                'email.Errors',
                'email.FeedParser',
                'email.Generator',
                'email.Header',
                'email.Iterators',
                'email.MIMEAudio',
                'email.MIMEBase',
                'email.MIMEImage',
                'email.MIMEMessage',
                'email.MIMEMultipart',
                'email.MIMENonMultipart',
                'email.MIMEText',
                'email.Message',
                'email.Parser',
                'email.Utils',
                'email._parseaddr',
                'email.base64',
                'email.base64MIME',
                'email.base64mime',
                'email.binascii',
                'email.cStringIO',
                'email.calendar',
                'email.charset',
                'email.codecs',
                'email.email',
                'email.encoders',
                'email.errors',
                'email.generator',
                'email.header',
                'email.iterators',
                'email.message',
                'email.mime',
                'email.os',
                'email.quopri',
                'email.quopriMIME',
                'email.quoprimime',
                'email.random',
                'email.re',
                'email.socket',
                'email.string',
                'email.sys',
                'email.time',
                'email.urllib',
                'email.utils',
                'email.uu',
                'email.warnings',
                'encodings',
                'encodings.__builtin__',
                'encodings.aliases',
                'encodings.codecs',
                'encodings.encodings',
                'ensurepip',
                'ensurepip.__future__',
                'ensurepip.os',
                'ensurepip.pkgutil',
                'ensurepip.shutil',
                'ensurepip.ssl',
                'ensurepip.sys',
                'ensurepip.tempfile',
                'errno',
                'exceptions',
                'filecmp',
                'fileinput',
                'fnmatch',
                'formatter',
                'fpformat',
                'fractions',
                'ftplib',
                'functools',
                'gc',
                'genericpath',
                'getopt',
                'getpass',
                'gettext',
                'glob',
                'gzip',
                'hashlib',
                'heapq',
                'hmac',
                'htmlentitydefs',
                'htmllib',
                'httplib',
                'ihooks',
                'imaplib',
                'imghdr',
                'imp',
                'importlib',
                'importlib.sys',
                'imputil',
                'inspect',
                'io',
                'ipyver',
                'itertools',
                'json',
                'json._json',
                'json.decoder',
                'json.encoder',
                'json.json',
                'json.re',
                'json.scanner',
                'json.struct',
                'json.sys',
                'keyword',
                'lib2to3',
                'libimport',
                'linecache',
                'locale',
                'logging',
                'logging.atexit',
                'logging.cStringIO',
                'logging.codecs',
                'logging.collections',
                'logging.os',
                'logging.sys',
                'logging.thread',
                'logging.threading',
                'logging.time',
                'logging.traceback',
                'logging.warnings',
                'logging.weakref',
                'macpath',
                'macurl2path',
                'mailbox',
                'mailcap',
                'markupbase',
                'marshal',
                'math',
                'md5',
                'mhlib',
                'mimetools',
                'mimetypes',
                'mimify',
                'modulefinder',
                'msvcrt',
                'multifile',
                'multiprocessing',
                'multiprocessing._multiprocessing',
                'multiprocessing.atexit',
                'multiprocessing.itertools',
                'multiprocessing.multiprocessing',
                'multiprocessing.os',
                'multiprocessing.process',
                'multiprocessing.signal',
                'multiprocessing.subprocess',
                'multiprocessing.sys',
                'multiprocessing.threading',
                'multiprocessing.util',
                'multiprocessing.weakref',
                'mutex',
                'netrc',
                'new',
                'nntplib',
                'nt',
                'ntpath',
                'nturl2path',
                'numbers',
                'opcode',
                'operator',
                'optparse',
                'os',
                'os.path',
                'os2emxpath',
                'pdb',
                'pickle',
                'pickletools',
                'pipes',
                'pkgutil',
                'platform',
                'plistlib',
                'popen2',
                'poplib',
                'posixfile',
                'posixpath',
                'pprint',
                'profile',
                'pstats',
                'py_compile',
                'pyclbr',
                'pydoc',
                'pydoc_data',
                'quopri',
                'random',
                're',
                'repr',
                'rexec',
                'rfc822',
                'rlcompleter',
                'robotparser',
                'runpy',
                'sched',
                'select',
                'sets',
                'sgmllib',
                'sha',
                'shelve',
                'shlex',
                'shutil',
                'signal',
                'smtpd',
                'smtplib',
                'sndhdr',
                'socket',
                'sqlite3.clr',
                'sqlite3.sys',
                'ssl',
                'stat',
                'string',
                'struct',
                'subprocess',
                'sys',
                'tempfile',
                'textwrap',
                'thread',
                'threading',
                'time',
                'token',
                'tokenize',
                'traceback',
                'types',
                'unittest',
                'unittest.StringIO',
                'unittest.case',
                'unittest.collections',
                'unittest.difflib',
                'unittest.fnmatch',
                'unittest.functools',
                'unittest.loader',
                'unittest.main',
                'unittest.os',
                'unittest.pprint',
                'unittest.re',
                'unittest.result',
                'unittest.runner',
                'unittest.signal',
                'unittest.signals',
                'unittest.suite',
                'unittest.sys',
                'unittest.time',
                'unittest.traceback',
                'unittest.types',
                'unittest.util',
                'unittest.warnings',
                'unittest.weakref',
                'urllib',
                'urlparse',
                'user',
                'uu',
                'version',
                'warnings',
                'weakref',
                'xml',
                'xml._xmlplus',
                'xml.parsers',
                'xmllib',
                'xmlrpclib',
                'zipfile',
                'zipimport',
                'zlib'
            ]

    passed = list(set(passed))
    passed.sort()
    return ("',\n").join(["'" + pa for pa in passed])

# ---  passed direct (imported on import) ----
def Direct():
    '''
       passed direct (imported on import)

    '''
    direct = [
                'BaseHTTPServer',
                'Bastion',
                'CGIHTTPServer',
                'ConfigParser',
                'Cookie',
                'DocXMLRPCServer',
                'HTMLParser',
                'IronPython',
                'Queue',
                'System',
                'UserList',
                'UserString',
                'aifc',
                'anydbm',
                'argparse',
                'ast',
                'asynchat',
                'asyncore',
                'audiodev',
                'bdb',
                'binhex',
                'bisect',
                'calendar',
                'cgitb',
                'chunk',
                'clr',
                'cmd',
                'code',
                'codeop',
                'colorsys',
                'commands',
                'compileall',
                'cookielib',
                'copy',
                'csv',
                'ctypes',
                'decimal',
                'dircache',
                'distutils',
                'doctest',
                'dumbdbm',
                'dummy_thread',
                'dummy_threading',
                'email',
                'ensurepip',
                'filecmp',
                'fileinput',
                'formatter',
                'fpformat',
                'fractions',
                'ftplib',
                'getopt',
                'getpass',
                'gettext',
                'glob',
                'hmac',
                'htmlentitydefs',
                'htmllib',
                'ihooks',
                'imaplib',
                'imghdr',
                'importlib',
                'importlib.sys',
                'imputil',
                'inspect',
                'io',
                'ipyver',
                'json',
                'lib2to3',
                'libimport',
                'local',
                'locale',
                'logging',
                'macpath',
                'macurl2path',
                'mailbox',
                'mailcap',
                'marshal',
                'md5',
                'mhlib',
                'mimify',
                'modulefinder',
                'multifile',
                'multiprocessing',
                'mutex',
                'netrc',
                'new',
                'nntplib',
                'numbers',
                'optparse',
                'os',
                'os2emxpath',
                'pdb',
                'pickle',
                'pickletools',
                'pipes',
                'platform',
                'plistlib',
                'popen2',
                'poplib',
                'posixfile',
                'profile',
                'pstats',
                'py_compile',
                'pyclbr',
                'pydoc_data',
                'quopri',
                're',
                'rexec',
                'rlcompleter',
                'robotparser',
                'runpy',
                'sched',
                'sets',
                'sgmllib',
                'sha',
                'shelve',
                'shlex',
                'smtpd',
                'smtplib',
                'sndhdr',
                'sqlite3',
                'sre_compile',
                'sre_constants',
                'sre_parse',
                'statvfs',
                'stringold',
                'stringprep',
                'subprocess',
                'sunau',
                'sunaudio',
                'symbol',
                'sys',
                'tabnanny',
                'tarfile',
                'telnetlib',
                'this',
                'threading',
                'time',
                'timeit',
                'toaiff',
                'trace',
                'traceback',
                'unittest',
                'urllib2',
                'user',
                'uu',
                'uuid',
                'version',
                'wave',
                'webbrowser',
                'whichdb',
                'wsgiref',
                'xdrlib',
                'xml',
                'xmllib',
                'zipfile'
                
             ]
    direct = list(set(direct))
    direct.sort()
    return ("',\n").join(["'" + dirct for dirct in direct])

def Indirect():
    '''
       last manually update Indirect
       indirectly imported from a "direct" import depedancy

    '''
    indirect = [
                'SimpleHTTPServer',
                'SimpleXMLRPCServer',
                'SocketServer',
                'StringIO',
                'UserDict',
                '_LWPCookieJar',
                '_MozillaCookieJar',
                '__builtin__',
                '__future__',
                '__main__',
                '_abcoll',
                '_ast',
                '_bisect',
                '_codecs',
                '_collections',
                '_csv',
                '_ctypes',
                '_dummy__threading_local',
                '_dummy_threading',
                '_functools',
                '_heapq',
                '_io',
                '_locale',
                '_md5',
                '_random',
                '_sha',
                '_sha256',
                '_sha512',
                '_ssl',
                '_struct',
                '_subprocess',
                '_warnings',
                '_weakref',
                '_weakrefset',
                '_winreg',
                'abc',
                'array',
                'atexit',
                'base64',
                'binascii',
                'cPickle',
                'cStringIO',
                'cgi',
                'codecs',
                'collections',
                'contextlib',
                'copy',
                'copy_reg',
                'ctypes._ctypes',
                'ctypes._endian',
                'ctypes.ctypes',
                'ctypes.os',
                'ctypes.struct',
                'ctypes.sys',
                'datetime',
                'difflib',
                'dis',
                'distutils.sys',
                'email.Charset',
                'email.Encoders',
                'email.Errors',
                'email.FeedParser',
                'email.Generator',
                'email.Header',
                'email.Iterators',
                'email.MIMEAudio',
                'email.MIMEBase',
                'email.MIMEImage',
                'email.MIMEMessage',
                'email.MIMEMultipart',
                'email.MIMENonMultipart',
                'email.MIMEText',
                'email.Message',
                'email.Parser',
                'email.Utils',
                'email._parseaddr',
                'email.base64',
                'email.base64MIME',
                'email.base64mime',
                'email.binascii',
                'email.cStringIO',
                'email.calendar',
                'email.charset',
                'email.codecs',
                'email.email',
                'email.encoders',
                'email.errors',
                'email.generator',
                'email.header',
                'email.iterators',
                'email.message',
                'email.mime',
                'email.os',
                'email.quopri',
                'email.quopriMIME',
                'email.quoprimime',
                'email.random',
                'email.re',
                'email.socket',
                'email.string',
                'email.sys',
                'email.time',
                'email.urllib',
                'email.utils',
                'email.uu',
                'email.warnings',
                'encodings',
                'encodings.__builtin__',
                'encodings.aliases',
                'encodings.codecs',
                'encodings.encodings',
                'ensurepip.__future__',
                'ensurepip.os',
                'ensurepip.pkgutil',
                'ensurepip.shutil',
                'ensurepip.ssl',
                'ensurepip.sys',
                'ensurepip.tempfile',
                'errno',
                'exceptions',
                'fnmatch',
                'functools',
                'gc',
                'genericpath',
                'gzip',
                'hashlib',
                'heapq',
                'httplib',
                'imp',
                'itertools',
                'json._json',
                'json.decoder',
                'json.encoder',
                'json.json',
                'json.re',
                'json.scanner',
                'json.struct',
                'json.sys',
                'keyword',
                'linecache',
                'locale',
                'logging.atexit',
                'logging.cStringIO',
                'logging.codecs',
                'logging.collections',
                'logging.os',
                'logging.sys',
                'logging.thread',
                'logging.threading',
                'logging.time',
                'logging.traceback',
                'logging.warnings',
                'logging.weakref',
                'markupbase',
                'math',
                'md5',
                'mimetools',
                'mimetypes',
                'msvcrt',
                'multiprocessing._multiprocessing',
                'multiprocessing.atexit',
                'multiprocessing.itertools',
                'multiprocessing.multiprocessing',
                'multiprocessing.os',
                'multiprocessing.process',
                'multiprocessing.signal',
                'multiprocessing.subprocess',
                'multiprocessing.sys',
                'multiprocessing.threading',
                'multiprocessing.util',
                'multiprocessing.weakref',
                'nt',
                'ntpath',
                'nturl2path',
                'opcode',
                'operator',
                'os.path',
                'pkgutil',
                'posixpath',
                'pprint',
                'pydoc',
                'random',
                'repr',
                'rfc822',
                'select',
                'sha',
                'shutil',
                'signal',
                'socket',
                'sqlite3.clr',
                'sqlite3.sys',
                'ssl',
                'stat',
                'string',
                'struct',
                'tempfile',
                'textwrap',
                'thread',
                'token',
                'tokenize',
                'types',
                'unittest.StringIO',
                'unittest.case',
                'unittest.collections',
                'unittest.difflib',
                'unittest.fnmatch',
                'unittest.functools',
                'unittest.loader',
                'unittest.main',
                'unittest.os',
                'unittest.pprint',
                'unittest.re',
                'unittest.result',
                'unittest.runner',
                'unittest.signal',
                'unittest.signals',
                'unittest.suite',
                'unittest.sys',
                'unittest.time',
                'unittest.traceback',
                'unittest.types',
                'unittest.util',
                'unittest.warnings',
                'unittest.weakref',
                'urllib',
                'urlparse',
                'warnings',
                'weakref',
                'xml._xmlplus',
                'xml.parsers',
                'xmlrpclib',
                'zipfile',
                'zipimport',
                'zlib'

               ]

    indirect = list(set(indirect))
    indirect.sort()
    return ("',\n").join(["'" + ind for ind in indirect])

def NotTested():
    '''
      **NOT TESTED**
      The following least common ancestor libs may have
      buggy behavior that will not load in an environment
      without IronPython/Python present

    '''
    notTested = [
                    'from ctypes import macholib',
                    'from ctypes import util',
                    'from ctypes import wintypes',
                    'from ctypes.macholib import  dylib',
                    'from ctypes.macholib import dyld',
                    'from ctypes.macholib import framework',
                    'from distutils import archive_util',
                    'from distutils import bcppcompiler',
                    'from distutils import ccompiler',
                    'from distutils import cmd as dstucmd',
                    'from distutils import config as dstuconfig',
                    'from distutils import core',
                    'from distutils import cygwinccompiler',
                    'from distutils import debug',
                    'from distutils import dep_util',
                    'from distutils import dir_util',
                    'from distutils import dist',
                    'from distutils import emxccompiler',
                    'from distutils import errors',
                    'from distutils import extension',
                    'from distutils import fancy_getopt',
                    'from distutils import file_util',
                    'from distutils import filelist',
                    'from distutils import log',
                    'from distutils import msvccompiler',
                    'from distutils import spawn',
                    'from distutils import sysconfig',
                    'from distutils import text_file',
                    'from distutils import unixccompiler',
                    'from distutils import util as dstutil',
                    'from distutils import version',
                    'from distutils import versionpredicate',
                    'from distutils.command import  bdist',
                    'from distutils.command import  bdist_dumb',
                    'from distutils.command import  bdist_rpm',
                    'from distutils.command import  bdist_wininst',
                    'from distutils.command import  build',
                    'from distutils.command import  build_clib',
                    'from distutils.command import  build_ext',
                    'from distutils.command import  build_py',
                    'from distutils.command import  build_scripts',
                    'from distutils.command import  check',
                    'from distutils.command import  clean',
                    'from distutils.command import  config',
                    'from distutils.command import  install',
                    'from distutils.command import  install_data',
                    'from distutils.command import  install_egg_info',
                    'from distutils.command import  install_headers',
                    'from distutils.command import  install_lib',
                    'from distutils.command import  install_scripts',
                    'from distutils.command import  register',
                    'from distutils.command import  sdist',
                    'from distutils.command import  upload',
                    'from dom import NodeFilter',
                    'from dom import domreg',
                    'from dom import minicompat',
                    'from dom import minidom',
                    'from dom import pulldom',
                    'from dom import xmlbuilder',
                    'from dummy import connection as dumbconn',
                    'from email import errors as emlerrs',
                    'from email import feedparser',
                    'from email import parser',
                    'from encodings import ascii',
                    'from encodings import base64_codec',
                    'from encodings import bz2_codec',
                    'from encodings import charmap',
                    'from encodings import cp037',
                    'from encodings import cp1006',
                    'from encodings import cp1026',
                    'from encodings import cp1140',
                    'from encodings import cp1250',
                    'from encodings import cp1251',
                    'from encodings import cp1252',
                    'from encodings import cp1253',
                    'from encodings import cp1254',
                    'from encodings import cp1255',
                    'from encodings import cp1256',
                    'from encodings import cp1257',
                    'from encodings import cp1258',
                    'from encodings import cp424',
                    'from encodings import cp437',
                    'from encodings import cp500',
                    'from encodings import cp720',
                    'from encodings import cp737',
                    'from encodings import cp775',
                    'from encodings import cp850',
                    'from encodings import cp852',
                    'from encodings import cp855',
                    'from encodings import cp856',
                    'from encodings import cp857',
                    'from encodings import cp858',
                    'from encodings import cp860',
                    'from encodings import cp861',
                    'from encodings import cp862',
                    'from encodings import cp863',
                    'from encodings import cp864',
                    'from encodings import cp865',
                    'from encodings import cp866',
                    'from encodings import cp869',
                    'from encodings import cp874',
                    'from encodings import cp875',
                    'from encodings import hex_codec',
                    'from encodings import hp_roman8',
                    'from encodings import idna',
                    'from encodings import iso8859_1',
                    'from encodings import iso8859_10',
                    'from encodings import iso8859_11',
                    'from encodings import iso8859_13',
                    'from encodings import iso8859_14',
                    'from encodings import iso8859_15',
                    'from encodings import iso8859_16',
                    'from encodings import iso8859_2',
                    'from encodings import iso8859_3',
                    'from encodings import iso8859_4',
                    'from encodings import iso8859_5',
                    'from encodings import iso8859_6',
                    'from encodings import iso8859_7',
                    'from encodings import iso8859_8',
                    'from encodings import iso8859_9',
                    'from encodings import koi8_r',
                    'from encodings import koi8_u',
                    'from encodings import latin_1',
                    'from encodings import mac_arabic',
                    'from encodings import mac_centeuro',
                    'from encodings import mac_croatian',
                    'from encodings import mac_cyrillic',
                    'from encodings import mac_farsi',
                    'from encodings import mac_greek',
                    'from encodings import mac_iceland',
                    'from encodings import mac_latin2',
                    'from encodings import mac_roman',
                    'from encodings import mac_romanian',
                    'from encodings import mac_turkish',
                    'from encodings import mbcs',
                    'from encodings import palmos',
                    'from encodings import ptcp154',
                    'from encodings import punycode',
                    'from encodings import quopri_codec',
                    'from encodings import raw_unicode_escape',
                    'from encodings import rot_13',
                    'from encodings import string_escape',
                    'from encodings import tis_620',
                    'from encodings import undefined',
                    'from encodings import unicode_escape',
                    'from encodings import unicode_internal',
                    'from encodings import utf_16',
                    'from encodings import utf_16_be',
                    'from encodings import utf_16_le',
                    'from encodings import utf_32',
                    'from encodings import utf_32_be',
                    'from encodings import utf_32_le',
                    'from encodings import utf_7',
                    'from encodings import utf_8',
                    'from encodings import utf_8_sig',
                    'from encodings import uu_codec',
                    'from encodings import zlib_codec',
                    'from ensurepip import __main__',
                    'from ensurepip import _uninstall',
                    'from etree import ElementInclude',
                    'from etree import ElementPath',
                    'from etree import ElementTree',
                    'from etree import SimpleXMLTreeBuilder',
                    'from fixes import fix_apply',
                    'from fixes import fix_asserts',
                    'from fixes import fix_basestring',
                    'from fixes import fix_buffer',
                    'from fixes import fix_callable',
                    'from fixes import fix_dict',
                    'from fixes import fix_except',
                    'from fixes import fix_exec',
                    'from fixes import fix_execfile',
                    'from fixes import fix_exitfunc',
                    'from fixes import fix_filter',
                    'from fixes import fix_funcattrs',
                    'from fixes import fix_future',
                    'from fixes import fix_getcwdu',
                    'from fixes import fix_has_key',
                    'from fixes import fix_idioms',
                    'from fixes import fix_import',
                    'from fixes import fix_imports',
                    'from fixes import fix_imports2',
                    'from fixes import fix_input',
                    'from fixes import fix_intern',
                    'from fixes import fix_isinstance',
                    'from fixes import fix_itertools',
                    'from fixes import fix_itertools_imports',
                    'from fixes import fix_long',
                    'from fixes import fix_map',
                    'from fixes import fix_metaclass',
                    'from fixes import fix_methodattrs',
                    'from fixes import fix_ne',
                    'from fixes import fix_next',
                    'from fixes import fix_nonzero',
                    'from fixes import fix_numliterals',
                    'from fixes import fix_operator',
                    'from fixes import fix_paren',
                    'from fixes import fix_print',
                    'from fixes import fix_raise',
                    'from fixes import fix_raw_input',
                    'from fixes import fix_reduce',
                    'from fixes import fix_renames',
                    'from fixes import fix_repr',
                    'from fixes import fix_set_literal',
                    'from fixes import fix_standarderror',
                    'from fixes import fix_sys_exc',
                    'from fixes import fix_throw',
                    'from fixes import fix_tuple_params',
                    'from fixes import fix_types',
                    'from fixes import fix_unicode',
                    'from fixes import fix_urllib',
                    'from fixes import fix_ws_comma',
                    'from fixes import fix_xrange',
                    'from fixes import fix_xreadlines',
                    'from fixes import fix_zip',
                    'from json import tool',
                    'from lib2to3 import __main__ as _23main_',
                    'from lib2to3 import btm_matcher',
                    'from lib2to3 import btm_utils',
                    'from lib2to3 import fixer_base',
                    'from lib2to3 import fixer_util',
                    'from lib2to3 import fixes',
                    'from lib2to3 import main',
                    'from lib2to3 import patcomp',
                    'from lib2to3 import pgen2',
                    'from lib2to3 import pygram',
                    'from lib2to3 import pytree',
                    'from lib2to3 import refactor',
                    'from logging import config as logconfig',
                    'from logging import handlers',
                    'from mine import application',
                    'from mine import audio',
                    'from mine import base',
                    'from mine import image',
                    'from mine import message as mnmsg',
                    'from mine import multipart',
                    'from mine import nonmultipart',
                    'from mine import text',
                    'from multiprocessing import connection',
                    'from multiprocessing import dummy',
                    'from multiprocessing import forking',
                    'from multiprocessing import heap',
                    'from multiprocessing import managers',
                    'from multiprocessing import pool',
                    'from multiprocessing import queues',
                    'from multiprocessing import reduction',
                    'from multiprocessing import sharedctypes',
                    'from multiprocessing import synchronize',
                    'from multiprocessing import util as mputil',
                    'from pgen2 import conv',
                    'from pgen2 import driver',
                    'from pgen2 import grammar',
                    'from pgen2 import literals',
                    'from pgen2 import parse',
                    'from pgen2 import pgen',
                    'from pgen2 import token as pgtokn',
                    'from pgen2 import tokenize as pgtoknz',
                    'from pydoc_data import topics',
                    'from sax import _exceptions',
                    'from sax import handler',
                    'from sax import saxutils',
                    'from sax import xmlreader',
                    'from sqlite3 import dbapi2',
                    'from sqlite3 import dump',
                    'from unittest import __main__ as _unittestmain',
                    'from unittest import main  as unittestmain',
                    'from unittest import util as ututil',
                    'from wsgiref import handlers',
                    'from wsgiref import headers',
                    'from wsgiref import simple_server',
                    'from wsgiref import util',
                    'from wsgiref import validate',
                    'from xml import dom',
                    'from xml import etree',
                    'from xml import sax',
                    'import MimeWriter'
                    
                   ]
    notTested = list(set(notTested))
    notTested.sort()
    return ("',\n").join(["'" + noT for noT in notTested])
#pylint: enable=bad-continuation
if __name__ == '__main__':
    pass
