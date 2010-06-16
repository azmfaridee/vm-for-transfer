#!/usr/bin/python

import xml.parsers.expat
from xml.parsers import xmlparser

class FileParser(xmlparser):
    def __init__(self):
        pass

class TransferFileParser(object):
    def StartElementHandler(self, file):
        print 'Start element:', name, attrs

    def EndElementHandler(self):
        print 'End element:', name

    def CharacterDataHandler(self):
        print 'Character data:', repr(data)

    def Parse(self, data, isfinal):
        return self.p.Parse(data, isfinal)
    
    def __init__(self, file):
        self.p = xml.parsers.expat.ParserCreate('utf-8')
        self.p.StartElementHandler = self.StartElementHandler
        self.p.EndElementHandler = self.EndElementHandler
        self.p.CharacterDataHandler = self.CharacterDataHandler

if __name__ == "__main__":
    print "Start"
    tfp = TransferFileParser('apertium-en-ca.en-ca.t1x')
    print "End"
