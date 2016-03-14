# Software License Agreement (BSD License)
#
# copyright (c) 2014-2015 imlint contributors
# all rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from imlint import cpplint
from imlint.cpplint import Match, IsBlankLine, main, FileInfo
from functools import partial

import os.path
import re

# Line length as per the Intermodalics C++ Style Guide
cpplint._line_length = 80


def patch(original_module):
    """ Decorator to easily allow wrapping/overriding of the Check* functions in cpplint. Should
        decorate a function which matches the signature of the function it replaces expect with
        the addition of a fn parameter, which is a pass-through of the replaced function, in case
        the replacement would like call through to the original functionality. """
    def wrap(override_fn):
        original_fn = getattr(original_module, override_fn.__name__)
        setattr(original_module, override_fn.__name__, partial(override_fn, original_fn))

        # Don't actually modify the function being decorated.
        return override_fn
    return wrap


def makeErrorFn(original_fn, suppress_categories, suppress_message_matches):
    """ Create a return a wrapped version of the error-report function which suppresses specific
        error categories. """
    def newError(filename, linenum, category, confidence, message):
        if category in suppress_categories:
            return
        if True in [bool(Match(r, message)) for r in suppress_message_matches]:
            return
        original_fn(filename, linenum, category, confidence, message)
    return newError


@patch(cpplint)
def GetHeaderGuardCPPVariable(fn, filename):
    """ Replacement for the function which determines the header guard variable, to pick one which
        matches Intermodalics C++ Style. """
    var_parts = list()
    head = filename
    while head:
        head, tail = os.path.split(head)
        var_parts.insert(0, tail)
        if head.endswith('include') or tail == "":
            break
        elif head.endswith('src'):
            if cpplint._root:
                var_parts.insert(0, cpplint._root)
            break
    return re.sub(r'[-./\s]', '_', "_".join(var_parts)).upper()


@patch(cpplint)
def CheckIncludeLine(fn, filename, clean_lines, linenum, include_state, error):
    """ Run the function to get include state, but suppress the prohibition on use of streams. """
    fn(filename, clean_lines, linenum, include_state,
       makeErrorFn(error, ['readability/streams'], []))
