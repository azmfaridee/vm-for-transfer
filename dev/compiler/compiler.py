from callstack import CallStack
from symboltable import SymbolTable
from expatparser import ExpatParser
from eventhandler import EventHandler
from compilerexception import CompilerException

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
        self.whenid = 0
        # otherwiseid, calculated from whenid but initially set to 0
        self.otherwiseid = 0
        self.actionid = 0

        # state variables
        self.MACRO_MODE = False
        
        self.APPEND_MODE = False
        self.appendModeArgs = 0

        self.NESTED_WHEN_MODE = False
        
        self.CONCAT_MODE = False
        self.concatModeArgs = 0
        
        # data structures
        # whenstack is used for nested when call
        self.whenStack = []
        self.otherwiseStack = []
        
        # callStack holds the call history
        self.callStack = CallStack()
        # parentRecord holds the child parent relationship
        ## self.parentRecord = ParentRecord()
        self.symbolTable = SymbolTable(self.callStack)

        # create the parse and the handler
        self.parser = ExpatParser(xmlfile, self)
        self.eventHandler = EventHandler(self)

        self.processedCode = []
        
        self.lazyBuffer = {}

    def compile(self):
        self.parser.parse()

    def optimize(self):
        if len(self.codestack) == 1:
            for line in self.codestack[0][2]:
                line = line.encode('utf-8')

                # optimization 1: remove placeholder instructions (#!#)
                ## if line.startswith('#!#'):
                ##     continue
                
                self.processedCode.append(line)
        else:
            raise CompilerException("FATAL ERROR:\n\tCannot optimize code, the code did not compile correctly!\n\tCurrent Codestack length: " + str(len(self.codestack)))

        
    def printCode(self):
        for line in self.processedCode:
            print line
            
    def printLabels(self):
        for label in self.labels:
            print label
