# -*- coding: utf-8 -*-
"""
.. created on Wed Feb 14 19:40:02 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""

def have():
    try:
        import clr
        print('Have clr as {}'.format(clr))
    except Exception as ex:
        print('Don"t have clr: Not in IronPython environment or ' + \
              'no ip/clr access')

    print('OK')

def hello():
    print('hello')
if __name__ == '__main__':
    have()
    hello()
