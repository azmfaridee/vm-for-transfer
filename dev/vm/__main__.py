#!/usr/bin/python

from trie import *
from vm import *
from transferword import *
import sys

class VMReader(object):
    """
    Class to read text vm instructions and convert that into
    code segment
    """
    def __init__(self, filename):
        self.cs = CodeSegment()
        with open(filename) as f:
            for line in f:
                ltext = line.strip()
                if len(ltext) == 0: continue
                else:
                    if ltext[0] == '#': continue
                    else:
                        ltext = ltext.split(':')
                        if len(ltext) == 2:
                            self.cs.add(ltext[1].strip(), ltext[0].strip())
                        else:
                            self.cs.add(ltext[0].strip())
        self.cs.link()

    def getCodeSegment(self):
        return self.cs

class InputReader(object):
    """
    TODO: apply unicode file reading capability
    """
    def __init__(self, filename):
        with open(filename) as f: self.text = f.read().strip()

if __name__ == "__main__":
    inr = InputReader('input-vm/stage1in.txt')

    # generate transfer words from source string
    twf = TransferWordFactory(inr.text)
    twf.generate()
    twords = twf.getTransferWords()

    # create the trie add the rules, this rules will be created from t1x files def-cat section
    t = Trie()

    vmreader = VMReader('input-vm/demo.vm')
    #vmreader = VMReader('apertium-en-ca.ca-en.v1m')
    cs = vmreader.getCodeSegment()
    
    s = VMStack()

    vm = VM(s, t, cs)
    vm.run()
    print s

    # example match againt source lang
    for tword in twords:
        print tword.slword, '->', t.find_relaxed(tword.slword.tags)
