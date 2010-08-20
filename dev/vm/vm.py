class VMStack(object):
    """
    The standard stack for the VM
    """
    def __init__(self):
        self.stack = []
    
    def push(self, data):
        self.stack.append(data)
    
    def pop(self):
        return self.stack.pop()
    
    def pop2(self):
        first = self.stack.pop()
        second = self.stack.pop()
        return first, second

    def top(self):
        return self.stack[-1]

    def __str__(self):
        return str(self.stack)

class CodeSegment(object):
    """
    Code segment for the VM, array index is used as the address of code line.
    VM uses PC (program counter) to browser through the code segment.
    """
    def __init__(self):
        self.labels = {}
        # we keep seperate unlinked, linked and optimized code for now for debug
        # purpose, in final implementaion there will be only one
        self.unlinked = []
        self.linked = []
        self.optimized = []

    def add(self, codestring, label=None):
        self.unlinked.append([codestring, label])
    
    def preprocess(self):
        for address, code in enumerate(self.unlinked):
            if code[1] is not None and code[1] not in self.labels:
                    self.labels[code[1]] = address

    def link(self):                    
        for code in self.unlinked:
            linkedcode = code[0]           
            for label, laddress in self.labels.iteritems():
                linkedcode = linkedcode.replace(label, str(laddress))
            self.linked.append(linkedcode)
    
    def optimize(self):
        self.optimized = self.linked
        
    # function for debugging purposes
    def printLabels(self):
        for x in self.labels: print x
    
    def printLinked(self):
        for x in self.linked: print x
    
    def printUnlinked(self):
        for x in self.unlinked: print x
        
    def printOptimized(self):
        for x in self.optimized: print x

class VMException(Exception):
    """
    Our basic exception for the VM
    # FIXME: more details
    """
    pass

class VM(object):
    """
    Class for the main virtual machine
    """
    def __init__(self, stack, trie, codesegment):
        self.vmstack = stack
        self.trie = trie
        self.codesegment = codesegment
        self.output = []
        self.pc = 0
        self.vars = {}
        self.a, self.b, self.c, self.d = [0 for x in range(0, 4)]
        
        self.one_opernad_instructions = [u'pushbl', u'pushz', u'pushnz', u'cliptl', u'clipsl', u'storetl', u'storesl', u'cmpi', u'cmp', u'match', u'matchi', u'hlt', u'ret', u'nop']
        self.two_operand_instructions = [u'push', u'pushv', u'pusht', u'pushsb', u'addtrie', u'lu', u'brace', u'chunk', u'out', u'jmp', u'jz', u'jnz', u'call']

    def run(self):
        try:
            while True:    
                print "RUNNING:", self.codesegment.linked[self.pc],
                # maxsplit is 1, because we have at most 2 operand instructions
                opcode = self.codesegment.linked[self.pc].split(None, 1)
                print 'LENGTH:', len(opcode)

                if len(opcode) == 1:
                    if opcode[0] == 'hlt': break
                    
                    elif opcode[0] == 'ret':
                        # restore vm state from state stack
                        
                        # get the return address
                        self.pc = int(self.vmstack.pop())
                        
                    else:
                        self.pc += 1

                elif len(opcode) == 2:
                    if opcode[0] == 'jmp':
                        self.pc = int(opcode[1])
                            
                    elif opcode[0] == 'call':
                        npar = int(vmstack.pop())
                        operands = []
                        for x in range(0, npar):
                            operands.append(int(vmstack.pop()))
                        self.vmstack.push(self.pc)
                        
                        # save currnet env and init new env with operands
                        self.pc = int(opcode[1].replace('"', ''))
                        
                    else:
                        self.pc += 1
                    ## call statement, for macro call
                    #if opcode[0] == 'call':
                    #    self.vmstack.push([self.a, self.b, self.c, self.d])
                    #    self.vmstack.push(self.pc + 1)
                    #    # FIXME: need fix in macro parameter number identification here
                    #    # push macro paramerters here
                    #    self.pc = int(opcode[1])
                        

                    ## general purpose push statement
                    #elif opcode[0] == 'push':
                    #    self.vmstack.push(opcode[1])
                    #    self.pc += 1
                    #
                    
                    ## declare a variable
                    #elif opcode[0] == 'var':
                    #    self.vars[opcode[1]] = None
                    #    self.pc += 1
                    ## assign value to a variable, stack has to be [(bottom) varname, value (top)]
                    #
                    
                    #elif opcode[0] == 'eq':
                    #    value, varname = self.vmstack.pop2()
                    #    if varname not in self.vars:
                    #        raise VMException('Undeclared variable referenced')
                    #    self.vars[varname] = value
                    #    self.pc += 1
                    
                    ## push a variable 'name' into the stack
                    ## used it prior to 'eq' opcode
                    #elif opcode[0] == 'pushv':
                    #    if opcode[1] not in self.vars:
                    #        raise VMException('Undeclared variable referenced')

                    # matches the last word in stack against trie
                    # STACK: word -> matched_symbol
                    #elif opcode[0] == 'match':
                    #    self.pc += 1
        except Exception, err:
            print str(err)
