class Word(object):
    """
    A single word, broken down to lemma and tags so that it can be processed 
    faster
    FIXME: 1. make sure '<' isn't part of the lemma, check for that
    """
    def __init__(self, word):
        self.word = word
        # superblank
        if word[0] == '[' or word[0] == '@':
            self.superblank = True
            self.lemma = self.word
            self.tags = ""
        # normal word
        else:
            self.superblank = False
            # check for empty word
            try:
                self.lemma = word[:word.index('<')]
                self.tags = reduce(lambda x, y: x + '.' + y, word[word.index('<')+1:-1].split('><'))
            except ValueError:
                self.lemma = self.tags = ""

    def __str__(self):
        return self.lemma + ':' +  self.tags

class TransferWord(object):
    """
    Consistes of source lang word, target lang word and immediately
    following blank(s)
    """
    def __init__(self, slword, tlword):
        self.slword = Word(slword)
        self.tlword = Word(tlword)
        # a transferword can have several superblanks following, so use a list
        self.blanks = []

    #def __str__(self):
    def __repr__(self):
        # not a good practice, but still it will do
        return "SL: " + str(self.slword) + ", TL: " + str(self.tlword) + ", Blank: " + str(self.blanks)    

class TransferWordFactory(object):

    def __init__(self, inr):
        self.string = inr.text
        self.transferwords = []

    def generate(self):
        while self.string:
            # superblank
            if self.string[0] == '[':
                startidx = 0
                endidx = self.string.index(']') + self.string[self.string.index(']'):].index('$')
                blank = self.string[startidx:endidx]
                # if the blank is the first item, create a dummy transferword
                if len(self.transferwords) == 0:
                    self.transferwords.append(TransferWord("", ""))
                # append this blank to last TransferWord's history
                self.transferwords[-1].blanks.append(TransferWord(*blank.split('/')))
            # normal transferword
            else:
                startidx = self.string.index('^') + 1
                endidx = self.string.index('$')
                part = self.string[startidx:endidx]
                self.transferwords.append(TransferWord(*part.split('/')))

            self.string = self.string[endidx+1:]

            
    def getTransferWords(self):
        return self.transferwords
