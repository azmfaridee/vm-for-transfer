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
                    # skip the comments
                    if ltext[0] == '#': continue
                    else:
                        ltext = ltext.split(':')
                        if len(ltext) == 2:
                            # the line is label: instruction
                            # we add in (instruction, label) format
                            self.cs.add(ltext[1].strip(), ltext[0].strip())
                        else:
                            # the line is instruction
                            self.cs.add(ltext[0].strip())
                            
        # do preprocessing of the code
        self.cs.preprocess()        
        # do the actual linking, removing labels with internal address
        self.cs.link()
        # do optimization
        self.cs.optimize()

    def getCodeSegment(self):
        return self.cs

class InputReader(object):
    """
    TODO: apply unicode file reading capability
    """
    def __init__(self, filename):
        with open(filename) as f:
            self.text = f.read().strip()

if __name__ == "__main__":
    inr = InputReader('input-vm/stage1in.txt')

    # generate transfer words from source string
    twf = TransferWordFactory(inr)
    twf.generate()
    twords = twf.getTransferWords()

    # create the trie add the rules, this rules will be created from t1x files def-cat section
    t = Trie()

    #vmreader = VMReader('input-vm/demo.vm')
    #vmreader = VMReader('apertium-en-ca.ca-en.v1m')
    vmreader = VMReader('input-vm/addtrie.v1m')
    cs = vmreader.getCodeSegment()
    
    #cs.printOptimized()
    
    
    s = VMStack()
    
    vm = VM(s, t, cs)
    vm.run()
    print s 
    
    ## example match againt source lang
    #for tword in twords:
    #    print tword.slword, '->', t.find_relaxed(tword.slword.tags)
