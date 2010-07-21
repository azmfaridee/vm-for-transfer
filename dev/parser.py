import xml.parsers.expat, sys, codecs
from pprint import pprint

skip_tags = ['cat-item', 'def-cat', 'section-def-cats', 'attr-item', 'def-attr', 'section-def-attrs', 'def-var', 'list-item', 'def-list', 'section-def-vars', 'section-def-lists']

leaf_tags = ['clip', 'lit', 'lit-tag', 'with-param', 'var',  'b', 'list', 'pattern-item']

# clip, lit-tag need special handling if inside of any of these tags
delayed_tags = ['let', 'modify-case']

DEBUG_MODE = True

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

    # kept for furture use only
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

            handler = self.compiler.eventHandler
            method_name = 'handle_' + name.replace('-', '_') + '_end'
            if hasattr(handler, method_name):
                method = getattr(handler, method_name)
                method(record, codebuffer)


            self.compiler.codestack.append([callStackLength, name, codebuffer])
            
        
        #print 'END',  self.callStack
        #print 'END2', self.parentRecord
        #print

        self.parentRecord.delRecord(record)
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

    def getChilds(self, parent):
        try:
            childs = self.childs[parent.name]
        except KeyError:
            childs = None
        return childs
 
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

    def hasEvent(self, findevent):
        for event in reversed(self.stack):
            if event == findevent:
                return True
        return False

    def hasEventNamed(self, name):
        for event in reversed(self.stack):
            if event.name == name:
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
        self.macroMode = True
        
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
        self.compiler.whenid += 1
        self.compiler.whenStack.append(self.compiler.whenid)
        
        label = u'when_' + str(self.compiler.whenStack[-1]) + u'_start'
        self.labels.append(label)
        code = [label + ':	nop']
        self.codestack.append([self.callStack.getLength(), 'when', code])

    def __get_xml_tag(self, event):
        tag = '<' + event.name
        for attr in event.attrs.keys():
            tag +=  ' ' + attr + '="' + event.attrs[attr] + '"'
        tag += '/>'
        return tag

    def __get_clip_tag_basic_code(self, event):
        code = []
        regex = ''
        
        if event.attrs['part'] not in ['lem', 'lemh', 'lemq', 'whole', 'tags']:
            # does optimization help? need to check that
            regex = reduce(lambda x, y: x + '|' + y, self.compiler.def_attrs[event.attrs['part']])
        else:
            # FIXME: the regex might not work
            if event.attrs['part'] == 'lem':
                regex = '\w'
            elif event.attrs['part'] == 'lemh':
                regex = '^\w'            
            elif event.attrs['part'] == 'lemq':
                regex = '#(\s\w)+'            
            elif event.attrs['part'] == 'whole':
                regex = '\\h'            
            elif event.attrs['part'] == 'tags':
                regex = '\\t'

        if DEBUG_MODE:
            code.append('### DEBUG: ' + self.__get_xml_tag(event))
        # push pos
        code.append('push\t' + event.attrs['pos'])
        # push regex
        code.append('push\t' + regex)

        return code

    def __get_clip_tag_lvalue_code(self, event):
        # rvalue code, we want to 'write' new value into clip
        code = []
        if event.attrs['side'] == 'sl': code.append(u'storesl')
        elif event.attrs['side'] == 'tl': code.append(u'storetl')
        return code
    
    def __get_clip_tag_rvalue_code(self, event):
        # rvalue code, we want to 'read' clip's value
        code = []
        if event.attrs['side'] == 'sl': code.append(u'clipsl')
        elif event.attrs['side'] == 'tl': code.append(u'cliptl')
        return code
    
    def handle_clip_start(self, event):
    #def handle_clip_start(self, event, internal_call = False, called_by = None):        
        if True in map(self.compiler.callStack.hasEventNamed, delayed_tags):
            # silently return, when inside delayed tags
            return

        code = self.__get_clip_tag_basic_code(event)

        # code for lvalue or rvalue calculation (i.e. 'clip' mode or 'store' mode)
        #parent =  self.compiler.callStack.getTop(2)
        # NOTE: siblings also include the curret tag
        #siblings =  self.compiler.parentRecord.getChilds(parent)
        
        # normal rvalue mode, we read clip's code
        ## if event.attrs['side'] == 'sl': code.append(u'clipsl')
        ## elif event.attrs['side'] == 'tl': code.append(u'cliptl')
        code.extend(self.__get_clip_tag_rvalue_code(event))
        
        self.codestack.append([self.callStack.getLength(), 'clip', code])

        # other misc tasks
        self.__check_for_append_mode()

    def __get_lit_tag_basic_code(self, event):
        code = []
        if DEBUG_MODE:
            code.append('### DEBUG: ' + self.__get_xml_tag(event))
        code.append('push\t' + '<' + event.attrs['v'] + '>')        
        return code

    def handle_lit_tag_start(self, event):
        if True in map(self.compiler.callStack.hasEventNamed, delayed_tags):
            return
        code = self.__get_lit_tag_basic_code(event)
        self.codestack.append([self.callStack.getLength(), 'lit-tag', code])

        # other misc tasks
        self.__check_for_append_mode()
        

    def __get_lit_basic_code(self, event):
        # FIXME: fix the problem with empty lit e.g. <lit v=""/>
        # print 'DEBUG push', event.attrs['v'].encode('utf-8')
        code = []
        if DEBUG_MODE:
            code.append('### DEBUG: ' + self.__get_xml_tag(event))        
        code.append('push\t' + event.attrs['v'])
        return code
    
    def handle_lit_start(self, event):
        if True in map(self.compiler.callStack.hasEventNamed, delayed_tags):
            return        
        code = self.__get_lit_basic_code(event)
        self.codestack.append([self.callStack.getLength(), 'lit-tag', code])

        # other misc tasks
        self.__check_for_append_mode()


    def __get_var_basic_code(self, event):
        code = []
        if DEBUG_MODE:
            code.append('### DEBUG: ' + self.__get_xml_tag(event))                
        code.append('pushv\t' + event.attrs['n'])
        return code
    
    def handle_var_start(self, event):
        if True in map(self.compiler.callStack.hasEventNamed, delayed_tags):
            return       
        code = self.__get_var_basic_code(event)
        self.codestack.append([self.callStack.getLength(), 'var', code])

    def handle_append_start(self, event):
        self.compiler.APPEND_MODE = True
        code = []
        if DEBUG_MODE:
            code.append('### DEBUG: ' + self.__get_xml_tag(event))
        code.append('push\t' +  event.attrs['n'])
        self.codestack.append([self.callStack.getLength(), 'append', code])
    

    # list of 'ending' event handlers
    def handle_and_end(self, event, codebuffer):
        codebuffer.append('and')

    def handle_or_end(self, event, codebuffer):
        codebuffer.append('or')

    def handle_not_end(self, event, codebuffer):
        codebuffer.append('not')

    def handle_equal_end(self, event, codebuffer):
        try:
            if event.attrs['caseless'] == 'yes':
                codebuffer.append(u'cmpi')
        except KeyError:
            codebuffer.append(u'cmp')
        
    def handle_begings_with_end(self, event, codebuffer):
        #codebuffer.append('#dummy begins-with')
        pass

    def handle_ends_with_end(self, event, codebuffer):
        #codebuffer.append('#dummy ends-with')
        pass

    def handle_contains_substring_end(self, event, codebuffer):
        #codebuffer.append('#dummy contains_substring')
        pass

    def handle_in_end(self, event, codebuffer):
        pass

    def handle_def_macro_end(self, event, codebuffer):
        label = u'macro_' + event.attrs['n'] + u'_end'
        codebuffer.append(label + '	:ret')
        self.labels.append(label)
        self.macroMode = False

    def handle_choose_end(self, event, codebuffer):
        pass

    def handle_when_end(self, event, codebuffer):
        label = u'when_' + str(self.compiler.whenStack[-1]) + u'_end'
        self.labels.append(label)
        codebuffer.append(label + ':\tnop')
        
        #self.compiler.whenid += 1
        self.compiler.whenStack.pop()

    def handle_test_end(self, event, codebuffer):
        # FIXME: this will probably not work in case of nested 'when' and 'otehrwise'
        # need to find something more mature
        codebuffer.append(u'jnz	when_' + str(self.compiler.whenStack[-1]) + '_end')


    # the followings are delayed mode tags
    def handle_let_end(self, event, codebuffer):
        child1, child2 = self.compiler.parentRecord.getChilds(event)
        code = []
        if child1.name == 'clip':
            code = self.__get_clip_tag_basic_code(child1)
            if child2.name == 'lit-tag':
                code.extend(self.__get_lit_tag_basic_code(child2))
            elif child2.name == 'lit':
                code.extend(self.__get_lit_basic_code(child2))
            elif child2.name == 'var':
                code.extend(self.__get_var_basic_code(child2))
            elif child2.name == 'clip':
                code.extend(self.__get_clip_tag_basic_code(child2))
                # normal rvalue cliptl or clipsl for 'clip'
                code.extend(self.__get_clip_tag_rvalue_code(child2))
                

            # storetl or storesl
            code.extend(self.__get_clip_tag_lvalue_code(child1))

        if child1.name == 'var':
            # 'var' here is lvalue, so need special care
            code.append('push\t' + child1.attrs['n'])
            if child2.name == 'clip':
                code.extend(self.__get_clip_tag_basic_code(child2))
                # normal rvalue cliptl or clipsl for 'clip'
                code.extend(self.__get_clip_tag_rvalue_code(child2))
            elif child2.name == 'lit-tag':
                code.extend(self.__get_lit_tag_basic_code(child2))
            elif child2.name == 'lit':
                code.extend(self.__get_lit_basic_code(child2))
            elif child2.name == 'var':
                code.extend(self.__get_var_basic_code(child2))

            # now the extra instuction for the assignment
            code.append('storev')
            

        codebuffer.extend(code)

    def handle_modify_case_end(self, event, codebuffer):
        child1, child2 = self.compiler.parentRecord.getChilds(event)
        code = []
        ## print child1
        ## print child2

    def handle_append_end(self, event, codebuffer):
        codebuffer.append('push\t' + str(self.compiler.appendModeArgs))
        codebuffer.append('appendv')

        # reset the state variables regarding append mode
        self.compiler.appendModeArgs = 0
        self.compiler.APPEND_MODE = False

    def __check_for_append_mode(self):
        if self.compiler.APPEND_MODE == True:
            self.compiler.appendModeArgs += 1
    
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
    """
    This is actually a container class that abstracts the underlying logic
    for the compilation process
    """
    def __init__(self, xmlfile):
        # various lists
        self.def_cats = {}
        self.def_attrs = {}
        self.variables = {}
        self.def_lists = {}

        self.labels = []
        self.codestack = []

        # id variables use for labeling, these need to be incremented
        self.whenid = 1

        # state variables
        self.MACRO_MODE = False
        
        self.APPEND_MODE = False
        self.appendModeArgs = 0

        self.NESTED_WHEN_MODE = False
        
        # data structures
        # callStack holds the call history
        self.callStack = CallStack()
        # parentRecord holds the child parent relationship
        self.parentRecord = ParentRecord()
        # whenstack is used for nested when call
        self.whenStack = []

        # create the parse and the handler
        self.parser = ExpatParser(xmlfile, self)
        self.eventHandler = EventHandler(self)

    def compile(self):
        self.parser.parse()

    def optimize(self):
        pass

    def printCode(self):
        if len(self.codestack) == 1:
            for line in self.codestack[0][2]:
                print line.encode('utf-8')

    def printLabels(self):
        for label in self.labels:
            print label

if __name__ == '__main__':
    inputfile = 'input-compiler/set1.t1x'
    compiler = Compiler(inputfile)
    compiler.compile()
    #print compiler.def_cats
    #print compiler.variables
    #print compiler.def_attrs
    #print compiler.def_lists
    compiler.printCode()
    #compiler.printLabels()
