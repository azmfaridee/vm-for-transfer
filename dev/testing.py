#!/usr/bin/python

# all the test are in this file
# FIXME: break down this file into modules
# FIXME: use unit testing

from transferword import *
import re
from trie import Trie

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
        print _chop(x)

def _chop(s):
    # the pattern must also be raw for the same reason
    l = []
    while s:
        m = re.compile(r'^((\\w)|(\\t)|(\s+)|(\w)|(<\w+>))', re.LOCALE | re.UNICODE).match(s)
        if m is not None:
            l.append(m.group())
            s = s[len(m.group()):]
    return l


def test_trie():
    print "Testing trie"
    t = Trie()

if __name__ == "__main__":
    try:
        print "Beginning test\n------------------------"
        ## test_transferword()
        ## test_chop()
        test_trie()
        print "------------------------\nTest successfully completed"
    except Exception, e:
        print "Error:", e
        print "Test aborted due to error"
