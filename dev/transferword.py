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
