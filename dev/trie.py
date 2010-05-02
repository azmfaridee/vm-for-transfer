#!/usr/bin/python
# Originally written by James Tauber http://jtauber.com/ 
# Modified by Abu Zaher Md. Faridee

from pprint import pprint

class Trie:
    """
    A Trie is like a dictionary in that it maps keys to values. However,
    because of the way keys are stored, it allows look up based on the
    longest prefix that matches.
    """

    def __init__(self):
        self.root = [None, {}]
    
    def __str__(self):
        return str(self.root)


    def add(self, key, value):
        """
        Add the given value for the given key.
        """
        
        key = key.split('.')        
        curr_node = self.root
        for symbol in key:
            curr_node = curr_node[1].setdefault(symbol, [None, {}])
        curr_node[0] = value


    def find_exact(self, key):
        """
        Return the value for the given key or None if key not found.
        """
        
        key = key.split('.')
        curr_node = self.root
        for symbol in key:
            try:
                curr_node = curr_node[1][symbol]
            except KeyError:
                return None
        return curr_node[0]

    def find_relaxed(self, key):
        
        key = key.split('.')
        curr_node = self.root
        for symbol in key:
            try:
                curr_node = curr_node[1][symbol]
            except KeyError:
                try: 
                    curr_node[1]['*']
                    return curr_node[1]['*'][0]
                except:
                    return None
        return curr_node[0]


    def find_prefix(self, key):
        """
        Find as much of the key as one can, by using the longest
        prefix that has a value. Return (value, remainder) where
        remainder is the rest of the given string.
        """
        
        key = key.split('.')
        curr_node = self.root
        remainder = key
        for symbol in key:
            try:
#                print "Trying", symbol
                curr_node = curr_node[1][symbol]
            except KeyError:
                return (curr_node[0], remainder)
            remainder = remainder[1:]
        return (curr_node[0], remainder)


    def convert(self, keystring):
        """
        convert the given string using successive prefix look-ups.
        """
        
        valuestring = ""
        key = keystring.split('.')
        while key:
            value, key = self.find_prefix(key)
            if not value:
                return (valuestring, key)
            valuestring += value
        return (valuestring, key)
        
class Word:
    
    def __init__(self, word):
        self.word = word
        self.lemma = word[:word.index('<')]
        self.tags = reduce(lambda x, y: x + '.' + y, word[word.index('<')+1:-1].split('><'))

    def __str__(self):
        return self.lemma + ':' +  self.tags
        
if __name__ == "__main__": 

    # I eat rice
    # ^prpers<prn><subj><p1><mf><sg>$ ^eat<vblex><pres>$ ^rice<n><sg>$^.<sent>$
   
    t = Trie()


    # add the rule in the trie
    t.add('prn.subj.*', 'prn_subj')
    t.add('prn.*', 'prn_subj')

    t.add('vblex.past', 'verbcj')
    t.add('vblex.pres', 'verbcj')
    t.add('vblex.past.*', 'verbcj')
    t.add('vblex.pres.*', 'verbcj')

    t.add('n.*', 'nom')
    t.add('np.*', 'nom')

    t.add('sent', 'sent')

#    print(t)

    data = ['prpers<prn><subj><p1><mf><sg>', 'eat<vblex><pres>', 'rice<n><sg>', '.<sent>']

    for x in data:
        w = Word(x)
        print w.tags
        print t.find_relaxed(w.tags)
#        print t.find_prefix(w.tags)
