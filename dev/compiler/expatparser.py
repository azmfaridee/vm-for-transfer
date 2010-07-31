import xml.parsers.expat, sys, codecs
from event import Event

skip_tags = ['cat-item', 'def-cat', 'section-def-cats', 'attr-item', 'def-attr', 'section-def-attrs', 'def-var', 'list-item', 'def-list', 'section-def-vars', 'section-def-lists']

leaf_tags = ['clip', 'lit', 'lit-tag', 'with-param', 'var',  'b', 'list', 'pattern-item']


class ExpatParser(object):
    def __init__(self, fileName, compiler):
        self.fileName = fileName
        self.Parser = xml.parsers.expat.ParserCreate()
        self.Parser.CharacterDataHandler = self.handleCharData
        self.Parser.StartElementHandler = self.handleStartElement
        self.Parser.EndElementHandler = self.handleEndElement
        self.compiler = compiler
        self.callStack = self.compiler.callStack
        ## self.parentRecord = self.compiler.parentRecord

    def parse(self):
        try:
            xmlFile = codecs.open(self.fileName, 'r', 'utf-8')
            fileContent = xmlFile.read().encode('utf-8')
            self.Parser.Parse(fileContent)
        except IOError:
            print "FATAL ERROR: Cannot open the transfer file specified!"
            sys.exit(0)

    # kept for furture use only
    def handleCharData(self, data): pass
    
    def handleStartElement(self, name, attrs):
        global skip_tags
        event = Event(name, attrs)

        self.callStack.push(event)

        ## parent = self.callStack.getTop(2)
        ## if parent != None and name not in skip_tags:
        ##     #child = self.callStack.getTop()
        ##     #print "PARENT", parent, "\nCHILD", child
        ##     self.parentRecord.addRecord(parent, event)

        #print 'START', self.callStack
        #print 'START2', self.parentRecord
        #print

        # EXPERIMENTAL
        self.compiler.symbolTable.addSymbol(event)

        
        handler = self.compiler.eventHandler
        method_name = 'handle_' + name.replace('-', '_') + '_start'
        if hasattr(handler, method_name):
            method = getattr(handler, method_name)
            method(event)
    
    def handleEndElement(self, name):        
        event = self.callStack.getTop()

        if event.name not in skip_tags and event.name not in leaf_tags:
            ## print 'CODESTACK before POP', self.compiler.codestack
            
            callStackLength = self.callStack.getLength()
            codebuffer = []
                
            while len(self.compiler.codestack) > 0 and self.compiler.codestack[-1][0] > callStackLength:
                for statement in reversed(self.compiler.codestack[-1][2]):
                    codebuffer.insert(0, statement)
                self.compiler.codestack.pop(-1)

            ## print event
            ## print codebuffer
            ## print 'CODESTACK after POP', self.compiler.codestack
            ## print 'DATA TO APPEND', [callStackLength, name, codebuffer]
            ## print

            handler = self.compiler.eventHandler
            method_name = 'handle_' + name.replace('-', '_') + '_end'
            
            result = None
            if hasattr(handler, method_name):
                method = getattr(handler, method_name)
                result = method(event, codebuffer)
            if result == None:
                self.compiler.codestack.append([callStackLength, name, codebuffer])
            else:
                self.compiler.codestack.append([callStackLength, name, []])
                self.compiler.lazyBuffer[name] = result
            
        
        #print 'END',  self.callStack
        #print 'END2', self.parentRecord
        #print

        ## self.parentRecord.delRecord(event)
        self.callStack.pop()
