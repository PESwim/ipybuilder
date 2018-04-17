# -*- coding: utf-8 -*-
"""
.. created: on Sat Mar 03 14:53:09 2018
.. author: PE LLC peswin@mindspring.com
.. copyright: 2018, Howard Dunn. Apache 2.0 v2 licensed.

"""
from version import __version__
import sys
from cStringIO import StringIO
import traceback
import exceptions

PartialErrors = []

class FatalError(Exception):
    '''
      ipybuild Exception catcher

    '''
    def __init__(self, name, msg):
        assert getattr(exceptions, name), 'need built-in exception not {}' \
        .format(name)
        super(FatalError, self).__init__('{} - {}'.format(name, msg))

def nullPartialErrors():

    global PartialErrors
    PartialErrors = []

def partialError(ex, msg):
    '''
       Aggregates (sinks) non-fatal errors that *may* require a
       re-run with fix'

       :output: errors to consider [list]

    '''
    stdout_ = sys.stdout
    exc_type = None
    exc_value = None
    exc_traceback = None

    try:
        capturedOutput = StringIO()
        capturedOutput.truncate(0)
        capturedOutput.seek(0)
        sys.stdout = capturedOutput
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback, file=sys.stdout)
        capturedOutput.flush()
        PartialErrors.append([msg, capturedOutput.getvalue()])
        sys.stdout = stdout_
        capturedOutput.seek(0)
        capturedOutput.close()

    except Exception as exc:
        capturedOutput.close()
        capturedOutput = None
        sys.stdout = stdout_
        raise exc
    finally:
        if exc_type:
            del exc_type
        if exc_value:
            del exc_value
        if exc_traceback:
            del exc_traceback

    return msg

if __name__ == '__main__':
    pass
