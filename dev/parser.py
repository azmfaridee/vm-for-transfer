import xml.parsers.expat, sys, codecs

class ExpatParser(object):
    Parser = None
    fileName = ''
    compiler = None
    tags = []

    def __init__(self, fileName, compiler):
        self.fileName = fileName
        self.Parser = xml.parsers.expat.ParserCreate()
        self.Parser.CharacterDataHandler = self.handleCharData
        self.Parser.StartElementHandler = self.handleStartElement
        self.Parser.EndElementHandler = self.handleEndElement
        self.compiler = compiler

    def parse(self):
        try:
            xmlFile = codecs.open(self.fileName, 'r', 'utf-8')
            fileContent = xmlFile.read().encode('utf-8')
            self.Parser.Parse(fileContent)
        except IOError:
            print "ERROR: Cannot open the transfer file specified!"
            sys.exit(0)

    def handleCharData(self, data): pass
    
    def handleStartElement(self, name, attrs):
        event = Event(name, attrs)

        callStack = self.compiler.callStack
        callStack.push(event)

        print 'START', callStack
        print
        
        handler = self.compiler.eventHandler
        method_name = 'handle_' + name.replace('-', '_') + '_start'
        if hasattr(handler, method_name):
            method = getattr(handler, method_name)
            method(event)
    
    def handleEndElement(self, name):
        callStack = self.compiler.callStack
        topdata = callStack.getTop()

        print 'END',  callStack
        print
        
        callStack.pop()


class CallStack(object):
    stack = []

    def __init__(self):
        pass

    def push(self, event):
        self.stack.append(event)

    def getTop(self, index = 1):
        try:
            topdata = self.stack[-index]
        except IndexError:
            print >> sys.stderr, 'ERROR: Out of index access in stack'
            topdata = None
        return topdata

    def pop(self):
        try:
            self.stack.pop()
        except IndexError:
            print >> sys.stderr, 'ERROR: Out of index access in stack'

    def find(self, findevent):
        for event in reversed(self.stack):
            if event == findevent:
                return True
        return False

    def addChild(self, parent, child):
        for event in reversed(self.stack):
            if event == parent:
                event.addChild(child)

    def __repr__(self):
        return self.stack.__repr__()
    
class EventHandler(object):
    compiler = None
    
    def __init__(self, compiler):
        self.compiler = compiler

    def handle_transfer_start(self, event):
        #print 'Handling transfer'
        pass

    def handle_def_cat_start(self, event):
        #print 'Handlng def-cats'
        pass

class Event(object):
    name = ''
    attrs = {}
    childs = []

    def __init__(self, name, attrs):
        self.name = name
        self.attrs = attrs

    def __eq__(self, other):
        if self.name == other.name and self.attrs == other.attrs:
            return True
        return False

    def __repr__(self):
        return vars(self).__str__()
 
    def addChild(self, child):
        self.childs.append(child)
        

class Compiler(object):
    callStack = None
    eventHandler = None
    
    def __init__(self, xmlfile):
        self.parser = ExpatParser(xmlfile, self)
        self.eventHandler = EventHandler(self)
        self.callStack = CallStack()

    def compile(self):
        self.parser.parse()

    def optimize(self):
        pass


if __name__ == '__main__':
    inputfile = 'input-compiler/set3.t1x'
    compiler = Compiler(inputfile)
    compiler.compile()
