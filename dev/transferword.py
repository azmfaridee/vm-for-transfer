#!/usr/bin/python
from trie import *
from vm import *

class Word(object):
    """
    A single word, broken down to lemma and tags so that it can be processed 
    faster
    FIXME: 1. make sure '<' isn't part of the lemma, check for that
    """
    def __init__(self, word):
        self.word = word
        self.lemma = word[:word.index('<')]
        self.tags = reduce(lambda x, y: x + '.' + y, word[word.index('<')+1:-1].split('><'))

    def __str__(self):
        return self.lemma + ':' +  self.tags

class TransferWord(object):
    """
    Consistes of source lang word, target lang word and immediately
    following blank
    """
    def __init__(self, slword, tlword, blank):
        self.slword = Word(slword)
        self.tlword = Word(tlword)
        self.blank = blank

    def __str__(self):
        return "SL: " + str(self.slword) + ", TL: " + str(self.tlword)

class TransferWordFactory(object):

    def __init__(self, string):
        self.string = string
        self.transferwords = []

    def generate(self):
        while self.string:
            part = self.string[self.string.index('^')+1:self.string.index('$')]
            self.string = self.string[self.string.index('$')+1:]
            try:
                blank = self.string[:self.string.index('^')]
            except ValueError:
                blank = None
            slword, tlword = part.split('/')
            self.transferwords.append(TransferWord(slword, tlword, blank))
            
    def getTransferWords(self):
        return self.transferwords

    def getBlanks(self):
        return self.blanks

    
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
    twords = twf.getTransferWords()

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
