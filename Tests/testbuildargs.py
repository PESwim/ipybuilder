# -*- coding: utf-8 -*-
"""
.. created on Tue Mar 06 15:02:10 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""
noskip = True
skipno = True
TESTCMDARGS = [(['python', '..\ipybuild.py', ' ', 'make.py',
                 'make_assembly.json', 'mock\inst\zip_list.txt',
                 'listexe=[mock/buildreqt.txt, mock/buildreqts.txt]'],
                noskip),
               (['python', '..\ipybuild.py', ' ', 'maketest_config.config',
                 'make.py', 'mock\inst\\listdll.txt', 
                 'listzip=mock\\inst\\zip_list.txt',
                 "{'listexe':'mock\inst\\clexe.txt'}"],
                noskip),
               (['python', '..\ipybuild.py', '', 'appname', '.\\release',
                 'makeEXE=False', 'mock\\locate_list.txt',
                 'listzip=mock\\inst\\zip_list.txt'],
                noskip),
               (['python', '..\ipybuild.py', 'maketest_config.config',
                 'make.py', 'mock\inst\\listdll.txt', 'listzip = mock\inst\zip_list.txt',
                 '{"listexe":"mock\inst\clexe.txt"}'],
                noskip),
               (['python', '..\ipybuild.py', 'make_test_config.config',
                 'make.p', 'mock\inst\listdll.txt',
                 'listzip = mock\inst\zip\listzip.txt',
                 "{'listexe':'mock\inst\listexe.txt'}"],
                noskip),
               (['python', '..\ipybuild.py',
                 'mock\locate_list.txt', 'mock\inst\\zip_list.txt'],
                noskip),
               (['python', '..\ipybuild.py', 'mock/make.py', 'True'],
                noskip)
              ]

TESTMAINARGS = [[(' ', 'make.py', 'make_assembly.json',
                  'mock\inst\zip_list.txt',
                  'listexe=[mock/buildreqt.txt, mock/buildreqts.txt]'),
                 skipno],
                [(' ', 'maketest_config.config',
                  'mock/make.py', 'mock/inst/listdll.txt', 
                  'listzip=mock/inst/zip_list.txt',
                  "{'listexe':'mock\inst\\clexe.txt'}"),
                 skipno],
                [('', 'appname', '.\\release',
                  'makeEXE=False', 'mock/locate_list.txt',
                  'listzip=mock\inst\\zip_list.txt'),
                 skipno],
                [('maketest_config.config',
                  'make.py', 'mock\inst\\listdll.txt',
                  'listzip = mock\inst\zip_list.txt',
                  '{"listexe":"mock\inst\clexe.txt"}'),
                 skipno],
                [('make_test_config.config',
                  'make.p', 'mock\inst\listdll.txt',
                  'listzip = mock\inst\zip\listzip.txt',
                  "{'listexe':'mock\inst\listexe.txt'}"),
                 skipno],
                [('mock/locate_list.txt', 'mock\inst\\zip_list.txt'),
                 skipno],
                [('mock/make.py',),
                 skipno]
               ]
