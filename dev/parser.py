import xml.parsers.expat, sys, codecs

skip_tags = ['cat-item', 'def-cat', 'section-def-cats', 'attr-item', 'def-attr', 'section-def-attrs', 'def-var', 'list-item', 'def-list', 'section-def-vars', 'section-def-lists']


class ExpatParser(object):
    def __init__(self, fileName, compiler):
        self.fileName = fileName
        self.Parser = xml.parsers.expat.ParserCreate()
        self.Parser.CharacterDataHandler = self.handleCharData
        self.Parser.StartElementHandler = self.handleStartElement
        self.Parser.EndElementHandler = self.handleEndElement
        self.compiler = compiler
        self.callStack = self.compiler.callStack
        self.parentRecord = self.compiler.parentRecord

    def parse(self):
        try:
            xmlFile = codecs.open(self.fileName, 'r', 'utf-8')
            fileContent = xmlFile.read().encode('utf-8')
            self.Parser.Parse(fileContent)
        except IOError:
            print "FATAL ERROR: Cannot open the transfer file specified!"
            sys.exit(0)

    def handleCharData(self, data): pass
    
    def handleStartElement(self, name, attrs):
        global skip_tags
        event = Event(name, attrs)

        self.callStack.push(event)

        parent = self.callStack.getTop(2)
        if parent != None and name not in skip_tags:
            child = self.callStack.getTop()
            #print "PARENT", parent, "\nCHILD", child
            self.parentRecord.addRecord(parent, child)

        #print 'START', self.callStack
        #print 'START2', self.parentRecord
        #print

        
        handler = self.compiler.eventHandler
        method_name = 'handle_' + name.replace('-', '_') + '_start'
        if hasattr(handler, method_name):
            method = getattr(handler, method_name)
            method(event)
    
    def handleEndElement(self, name):        
        record = self.callStack.getTop()
        self.parentRecord.delRecord(record)

        #print 'END',  self.callStack
        #print 'END2', self.parentRecord
        #print

        self.callStack.pop()

class ParentRecord(object):
    def __init__(self):
        self.childs = {}

    def addRecord(self, parent, child):
        global skip_tags

        if parent.name not in skip_tags:
            if parent.name not in self.childs.keys():
                self.childs[parent.name] = []
            self.childs[parent.name].append(child)
				
    def delRecord(self, parent):
        try:
            del(self.childs[parent.name])
        except KeyError:
            pass
 
    def __repr__(self):
        return self.childs.__repr__()
 
        
class CallStack(object):
    def __init__(self):
        self.stack = []

    def push(self, event):
        self.stack.append(event)

    def getTop(self, index = 1):
        try:
            topdata = self.stack[-index]
        except IndexError:
            print >> sys.stderr, 'WARNING: Out of index access in stack'
            topdata = None
        return topdata

    def pop(self):
        try:
            self.stack.pop()
        except IndexError:
            print >> sys.stderr, 'WARNING: Out of index access in stack'

    def find(self, findevent):
        for event in reversed(self.stack):
            if event == findevent:
                return True
        return False

    def __repr__(self):
        return self.stack.__repr__()
    
class EventHandler(object):
    def __init__(self, compiler):
        self.compiler = compiler
        self.callStack = self.compiler.callStack

    def handle_transfer_start(self, event):
        #print 'Handling transfer'
        pass

    def handle_def_cat_start(self, event):
        #print 'Handlng def-cats'
        pass

class Event(object):
    def __init__(self, name, attrs):
        self.name = name
        self.attrs = attrs
        #self.childs = []

    def __eq__(self, other):
        if self.name == other.name and self.attrs == other.attrs:
            return True
        return False

    def __repr__(self):
        return vars(self).__str__()
 

class Compiler(object):
    def __init__(self, xmlfile):
        self.callStack = CallStack()
        self.parentRecord = ParentRecord()

        self.parser = ExpatParser(xmlfile, self)
        self.eventHandler = EventHandler(self)

    def compile(self):
        self.parser.parse()

    def optimize(self):
        pass


if __name__ == '__main__':
    inputfile = 'input-compiler/set1.t1x'
    compiler = Compiler(inputfile)
    compiler.compile() 
