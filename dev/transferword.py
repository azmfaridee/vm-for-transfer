#!/usr/bin/python
from pprint import pprint

class Word:
    def __init__(self, word):
        self.word = word
        self.lemma = word[:word.index('<')]
        self.tags = reduce(lambda x, y: x + '.' + y, word[word.index('<')+1:-1].split('><'))

    def __str__(self):
        return self.lemma + ':' +  self.tags


class TransferWord(object):
    def __init__(self, slword, tlword):
        self.slword = Word(slword)
        self.tlword = Word(tlword)

    def __str__(self):
        return "SL: " + str(self.slword) + ", TL: " + str(self.tlword)

class TransferWordFactory(object):
    """
    Not a factory in a true sense
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
 
# echo "I eat rice" | apertium -d . en-es-tagger
# ^prpers<prn><subj><p1><mf><sg>$ ^eat<vblex><pres>$ ^rice<n><sg>$^.<sent>$
# echo "I eat rice" | apertium -d . en-es-tagger | lt-proc -b en-es.autobil.bin
# ^prpers<prn><subj><p1><mf><sg>/prpers<prn><tn><p1><mf><sg>$ ^eat<vblex><pres>/comer<vblex><pres>$ ^rice<n><sg>/arroz<n><m><sg>$^.<sent>/.<sent>$

if __name__ == "__main__":
    string = "^prpers<prn><subj><p1><mf><sg>/prpers<prn><tn><p1><mf><sg>$ ^eat<vblex><pres>/comer<vblex><pres>$ ^rice<n><sg>/arroz<n><m><sg>$^.<sent>/.<sent>$"
    transferWordFactory = TransferWordFactory(string)
    transferWordFactory.generate()
    transferwords = transferWordFactory.getTransferWord()
