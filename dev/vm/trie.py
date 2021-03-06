#!/usr/bin/python
# Originally written by James Tauber http://jtauber.com/ 
# Modified by Abu Zaher Md. Faridee

import re

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


    def add(self, key, value, mode='normal'):
        """
        Add the given value for the given key.
        """

        if mode == 'normal': key = key.split('.')
        else: key = self._chop(key)
        curr_node = self.root
        for symbol in key:
            curr_node = curr_node[1].setdefault(symbol, [None, {}])
        curr_node[0] = value

    def _chop(self, s):
        """
        This function is used to tokenize the pattern, given pattern, returns a list
        of tokens that can be directly inserted into the trie and later matched against
        """
        l = []
        while s:
            # NOTE: the pattern must also be raw
            # FIXME: mouse<n><sg> -> m o u s e <n> <sg>
            #        .<sent> -> . <sent> --> need regex for this type of punctuation marks too
            m = re.compile(r'^((\\w)|(\\t)|(\s+)|[\w.;]|(<\w+>))', re.LOCALE | re.UNICODE).match(s)
            if m is not None:
                l.append(m.group())
                s = s[len(m.group()):]
        return l        

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

