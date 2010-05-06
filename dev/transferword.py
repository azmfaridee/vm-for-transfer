#!/usr/bin/python
from pprint import pprint
from trie import Trie

class Word(object):
    """
    A single word, broken down to lemma and tags so that it can be processed 
    faster
    FIXME: make sure '<' isn't part of the lemma, check for that
    """
    def __init__(self, word):
        self.word = word
        self.lemma = word[:word.index('<')]
        self.tags = reduce(lambda x, y: x + '.' + y, word[word.index('<')+1:-1].split('><'))

    def __str__(self):
        return self.lemma + ':' +  self.tags


class TransferWord(object):
    """
    Consistes of source lang word and target lang word
    """
    def __init__(self, slword, tlword):
        self.slword = Word(slword)
        self.tlword = Word(tlword)

    def __str__(self):
        return "SL: " + str(self.slword) + ", TL: " + str(self.tlword)

class TransferWordFactory(object):
    """
    Not a true facotory pattern IMHO
    """
    def __init__(self, string):
        self.string = string
        self.transferwords = []

    def generate(self):
        """
        FIXME: Very naive right now, discards blanks, will fix that later
        """
        while self.string:
            part = self.string[self.string.index('^')+1:self.string.index('$')]
            self.string = self.string[self.string.index('$')+1:]
            self.transferwords.append(TransferWord(*part.split('/')))
            
    def getTransferWord(self):
        return self.transferwords

class VMStack(object):
    """
    The standard stack for the VM
    """
    def __init__(self):
        self.stack = []
    
    def push(self, data):
        self.stack.append(data)
    
    def pop(self):
        return self.stack.pop()

    def top(self):
        return self.stack[-1]

    def __str__(self):
        return str(self.stack)

class CodeSegment(object):
    """
    Code segment for the VM, array index is used as the address of code line.
    VM uses PC (program counter) to browser through the code segment.
    """
    def __init__(self):
        self.labels = {}
        # we keep seperate unlinked, linked and optimized code for now for debug
        # purpose, in final implementaion there will be only one
        self.unlinked = []
        self.linked = []
        self.optimized = []

    def add(self, codestring, label=None):
        self.unlinked.append([codestring, label])

    def link(self):
        for address, code in enumerate(self.unlinked):
            if code[1] is not None and code[1] not in self.labels:
                    self.labels[code[1]] = address

            linkedcode = code[0]            
            for label, laddress in self.labels.iteritems():
                linkedcode = linkedcode.replace(label, str(laddress))
            self.linked.append(linkedcode)

class VM(object):
    """
    Class for the main virtual machine
    """
    def __init__(self, stack, trie, codesegment):
        self.vmstack = stack
        self.trie = trie
        self.codesegment = codesegment
        self.output = []
        self.pc = 0
        self.a, self.b, self.c, self.d = [0 for x in range(0, 4)]

    def run(self):
        while True:    
            print "RUNNING:", self.codesegment.linked[self.pc]
            opcode = self.codesegment.linked[self.pc].split(' ', 1)
            # for zero arg instruction
            if len(opcode) == 1:
                if opcode[0] == 'hlt': break
                if opcode[0] == 'return':
                    self.pc = self.vmstack.pop()
                    self.a, self.b, self.c, self.d = self.vmstack.pop()
                    
            # for 2 or more arg instruction
            else:
                if opcode[0] == 'jmp':
                    self.pc = int(opcode[1])
                elif opcode[0] == 'call':
                    self.vmstack.push([self.a, self.b, self.c, self.d])
                    self.vmstack.push(self.pc + 1)
                    # FIXME: need fix in macro parameter number identification here
                    # push macro paramerters here
                    self.pc = int(opcode[1])
                elif opcode[0] == 'push':
                    self.vmstack.push(opcode[1])
                    self.pc += 1
                else:
                    self.pc += 1
    
# echo "I eat rice" | apertium -d . en-es-tagger
# ^prpers<prn><subj><p1><mf><sg>$ ^eat<vblex><pres>$ ^rice<n><sg>$^.<sent>$
# echo "I eat rice" | apertium -d . en-es-tagger | lt-proc -b en-es.autobil.bin
# ^prpers<prn><subj><p1><mf><sg>/prpers<prn><tn><p1><mf><sg>$ ^eat<vblex><pres>/comer<vblex><pres>$ ^rice<n><sg>/arroz<n><m><sg>$^.<sent>/.<sent>$

if __name__ == "__main__":
    # source string, will be read from stdin
    string = "^prpers<prn><subj><p1><mf><sg>/prpers<prn><tn><p1><mf><sg>$ ^eat<vblex><pres>/comer<vblex><pres>$ ^rice<n><sg>/arroz<n><m><sg>$^.<sent>/.<sent>$"

    # generate transfer words from source string
    twf = TransferWordFactory(string)
    twf.generate()
    twords = twf.getTransferWord()

    # create the trie add the rules, this rules will be created from t1x files def-cat section
    t = Trie()
    t.add('prn.subj.*', 'prn_subj')
    t.add('prn.*', 'prn_subj')
    t.add('vblex.past', 'verbcj')
    t.add('vblex.pres', 'verbcj')
    t.add('vblex.past.*', 'verbcj')
    t.add('vblex.pres.*', 'verbcj')
    t.add('n.*', 'nom')
    t.add('np.*', 'nom')
    t.add('sent', 'sent')

    # example match againt source lang
#    for tword in twords:
#        print tword.slword.tags
#        print t.find_relaxed(tword.slword.tags)

    cs = CodeSegment()
    cs.add('push a', 'start')
    cs.add('push b', 'dummy')
#    cs.add('jmp start')
#    cs.('call macro1')
    cs.add('hlt')

    cs.link()
#    print cs.linked

    s = VMStack()

    vm = VM(s, t, cs)
    vm.run()
#    print s
