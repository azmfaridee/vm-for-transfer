import xml.parsers.expat, sys, codecs

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
            #child = self.callStack.getTop()
            #print "PARENT", parent, "\nCHILD", child
            self.parentRecord.addRecord(parent, event)

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

        if record.name not in skip_tags and record.name not in leaf_tags:
            #print 'CODESTACK before POP', self.compiler.codestack
            
            callStackLength = self.callStack.getLength()
            codebuffer = []

            while len(self.compiler.codestack) > 0 and self.compiler.codestack[-1][0] > callStackLength:
                for statement in reversed(self.compiler.codestack[-1][2]):
                    codebuffer.insert(0, statement)
                self.compiler.codestack.pop(-1)

            #print codebuffer
            #print 'CODESTACK after POP', self.compiler.codestack
            #print 'DATA TO APPEND', [callStackLength, name, codebuffer]
            #print

            self.compiler.codestack.append([callStackLength, name, codebuffer])
            
        
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

    def getLength(self):
        return len(self.stack)

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
        self.codestack = self.compiler.codestack
        self.labels = self.compiler.labels

    # list of 'starting' event handlers
    def handle_cat_item_start(self, event):
        def_cat = self.callStack.getTop(2)
        def_cat_id = def_cat.attrs['n']
        if def_cat_id not in self.compiler.def_cats.keys():
            self.compiler.def_cats[def_cat_id] = []

        # lemma is OPTIONAL in DTD
        if 'lemma' in event.attrs.keys():
            regex = event.attrs['lemma']
        else:
            regex = '\w'

        # tags is REQUIRED in DTD
        # but still for safety we're checking
        if 'tags' in event.attrs.keys():
            tags = event.attrs['tags'].split('.')
            for tag in tags:
                # FIXME: what to do in case of empty tags?
                if tag == '':
                    continue
                if tag == '*':
                    regex = regex + '\\t'
                    continue
                regex = regex + '<' + tag + '>'
        else:
            regex = regex + '\t'

        self.compiler.def_cats[def_cat_id].append(regex)

    def handle_attr_item_start(self, event):
        def_attr = self.callStack.getTop(2)
        def_attr_id = def_attr.attrs['n']
        if def_attr_id not in self.compiler.def_attrs.keys():
            self.compiler.def_attrs[def_attr_id] = []

        tags = event.attrs['tags'].split('.')
        regex = ''
        for tag in tags:
            regex = regex + '<' + tag + '>'

        self.compiler.def_attrs[def_attr_id].append(regex)

    def handle_def_var_start(self, event):
        vname = event.attrs['n']
        value = event.attrs.setdefault('v', '')
        self.compiler.variables[vname] = value

    def handle_list_item_start(self, event):
        def_list = self.callStack.getTop(2)
        def_list_id = def_list.attrs['n']

        if def_list_id not in self.compiler.def_lists.keys():
            self.compiler.def_lists[def_list_id] = []
        self.compiler.def_lists[def_list_id].append(event.attrs['v'])

    def handle_def_macro_start(self, event):
        # FIXME later, the macro mode
        macro_more = True

        macro_name = event.attrs['n']
        npar = int(event.attrs['npar'])
        label = 'macro_' + macro_name + '_start'

        # print macro_name
        self.labels.append(label)
        code = [label + ':	nop']
        self.codestack.append([self.callStack.getLength(), 'def-macro', code])

    def handle_choose_start(self, event):
        pass

    def handle_when_start(self, event):
        label = u'when_' + str(self.compiler.whenid) + u'_start'
        self.labels.append(label)
        code = [label + ':	nop']
        self.codestack.append([self.callStack.getLength(), 'when', code])

    def handle_clip_start(self, event):
        # URGENT FIX
        code = ['#dummy clip']
        self.codestack.append([self.callStack.getLength(), 'clip', code])

    def handle_lit_tag_start(self, event):
        # URGENT FIX
        code = ['#dummy lit-tag']
        self.codestack.append([self.callStack.getLength(), 'lit-tag', code])

    def handle_lit_start(self, event):
        code = ['push	' + event.attrs['v']]
        self.codestack.append([self.callStack.getLength(), 'lit-tag', code])
        

    # list of 'ending' event handlers
    def handle_and_end(self, event):
        #print event
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

        self.def_cats = {}
        self.def_attrs = {}
        self.variables = {}
        self.def_lists = {}

        self.labels = []
        self.codestack = []

        self.whenid = 1
        self.chooseid = 1
        
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
    #print compiler.def_cats
    #print compiler.variables
    #print compiler.def_attrs
    #print compiler.def_lists
    print compiler.codestack
