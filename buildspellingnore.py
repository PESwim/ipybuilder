from version import __version__# -*- coding: utf-8 -*-
"""
.. created on Sat Feb 24 23:29:13 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""

from enchant.checker import SpellChecker
chkr = SpellChecker("en_US")
SPI = 'buildSpellIgnore.txt'

def UniqueIgnore():
    '''
	    Organize spell check fails during pylint
    
    '''	   
    errs = []
    with open(SPI, 'r') as tr:
        spdic = tr.readlines()
    
    print(spdic)
    for ln in spdic:
        chkr.set_text(ln)
        for err in chkr:
            errs.append(err.word.strip())
    errs = list(set(errs))
    errs = '\n'.join(errs)

    with open(SPI, 'a') as ta:
        ta.write('\n')
        ta.writelines(errs)
    uerrs = []
    with open(SPI, 'r') as tr:
        sping = tr.readlines()

    for s in sping:
        uerrs.append(s.strip())
    uerrs = sorted(list(set(uerrs)))

    with open(SPI, 'w') as tw:
        tw.writelines(('\n').join(uerrs))
    #uerrs = ('\n').join(uerrs).split('\n')
    #print(('uerrs:' + '\n\t{}'*len(uerrs)).format(*uerrs))
if __name__ == '__main__':

    UniqueIgnore()
