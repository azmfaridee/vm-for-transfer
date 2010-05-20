#!/usr/bin/python

# all the test are in this file
# FIXME: break down this file into modules
# FIXME: use unit testing

from transferword import *
import re

def test_transferword():
    print "Testing transferword"
    string = "^This<det><dem><sg>/Este<det><dem><GD><sg>$[<lpar>$		^]^<rpar>/@<rpar>$^be<vbser><pri><p3><sg>/ser<vbser><pri><p3><sg>$"
    twf = TransferWordFactory(string)
    twf.generate()
    tw = twf.getTransferWords()
    for x in tw:
        print x


def test_chop():
    # text must be converted into raw format, otherwise \t will be
    # interpreted as tab
    l = [r'\w mouse<n><sg>\t', r'the<det>\t mouse<n><sg>\t']
    for x in l:
        _chop(x)

def _chop(s):
    try:
        # the pattern must also be raw for the same reason
        p = re.compile(r'^(\\w|\\t)')
        m = p.match(s)
        print s, m.group()
    except AttributeError, e:
        pass
    

if __name__ == "__main__":
    test_transferword()
    test_chop()
