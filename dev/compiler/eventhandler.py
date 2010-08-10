from codegenerator import CodeGenerator, DEBUG_MODE

# clip, lit-tag need special handling if inside of any of these tags
delayed_tags = ['let', 'modify-case']

class EventHandler(object):
    def __init__(self, compiler):
        self.compiler = compiler
        self.callStack = self.compiler.callStack
        self.codestack = self.compiler.codestack
        self.labels = self.compiler.labels
        self.codeGenerator = CodeGenerator(self.compiler)


    # list if private helper functions
    def __check_for_special_mode(self):
        if self.compiler.APPEND_MODE == True:
            self.compiler.appendModeArgs += 1
        if self.compiler.CONCAT_MODE == True:
            self.compiler.concatModeArgs += 1
          
    # function to generate cross prdouct,
    # used in pattern section
    def __cross(self, args):
        ans = [[]]
        for arg in args:
            ans = [x+[y] for x in ans for y in arg]
        return ans
            

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
        
    def handle_section_def_macros_start(self, event):
        label = u'section_def_macros_start'
        self.labels.append(label)
        
        code = []
        
        # at the start of program, jmp to rules section (all the addtrie are there by default)
        # basically this is where we tell the program where the MAIN section of the assembly code starts
        
        code.append(u'jmp\tsection_rules_start')
        code.append(label + ':\tnop')
        
        self.codestack.append([self.callStack.getLength(), 'section-def-macros', code])
        
    def handle_section_rules_start(self, event):
        label = u'section_rules_start'
        self.labels.append(label)
        code = [label + ':\tnop']
        self.codestack.append([self.callStack.getLength(), 'section-rules', code])

    def handle_def_macro_start(self, event):
        # FIXME later, the macro mode
        self.macroMode = True
        
        macro_name = event.attrs['n']
        npar = int(event.attrs['npar'])
        label = 'macro_' + macro_name + '_start'

        # print macro_name
        self.labels.append(label)
        code = [label + ':\tnop']
        self.codestack.append([self.callStack.getLength(), 'def-macro', code])

    def handle_choose_start(self, event):
        pass
        
    def handle_when_start(self, event):
        self.compiler.whenid += 1
        self.compiler.whenStack.append(self.compiler.whenid)
        
        label = u'when_' + str(self.compiler.whenStack[-1]) + u'_start'
        self.labels.append(label)
        code = [label + ':\tnop']
        self.codestack.append([self.callStack.getLength(), 'when', code])
        
    def handle_action_start(self, event):
        self.compiler.actionid += 1
    
    def handle_with_param_start(self, event):
        self.compiler.macro_args_count += 1

    def handle_otherwise_start(self, event):
        self.compiler.otherwiseStack.append(self.compiler.otherwiseid)
        label = u'otherwise_' + str(self.compiler.otherwiseStack[-1]) + u'_start'
        self.labels.append(label)
        code = [label + ':\tnop']
        self.codestack.append([self.callStack.getLength(), 'otherwise', code])

    
    def handle_clip_start(self, event):
        #def handle_clip_start(self, event, internal_call = False, called_by = None):
        #if True in map(self.compiler.callStack.hasEventNamed, delayed_tags):
        if True in map(self.compiler.callStack.hasImmediateParent, delayed_tags):
            # silently return, when inside delayed tags
            return

        code = self.codeGenerator.get_clip_tag_basic_code(event)

        # code for lvalue or rvalue calculation (i.e. 'clip' mode or 'store' mode)
        #parent =  self.compiler.callStack.getTop(2)
        # NOTE: siblings also include the curret tag
        #siblings =  self.compiler.parentRecord.getChilds(parent)
        
        # normal rvalue mode, we read clip's code
        ## if event.attrs['side'] == 'sl': code.append(u'clipsl')
        ## elif event.attrs['side'] == 'tl': code.append(u'cliptl')
        code.extend(self.codeGenerator.get_clip_tag_rvalue_code(event))
        
        self.codestack.append([self.callStack.getLength(), 'clip', code])

        # other misc tasks
        self.__check_for_special_mode()
        
    def handle_case_of_start(self, event):
        pass

    def handle_lit_tag_start(self, event):
        #if True in map(self.compiler.callStack.hasEventNamed, delayed_tags):
        if True in map(self.compiler.callStack.hasImmediateParent, delayed_tags):
            return
        code = self.codeGenerator.get_lit_tag_basic_code(event)
        self.codestack.append([self.callStack.getLength(), 'lit-tag', code])

        # other misc tasks
        self.__check_for_special_mode()
            
    def handle_lit_start(self, event):
        #if True in map(self.compiler.callStack.hasEventNamed, delayed_tags):
        if True in map(self.compiler.callStack.hasImmediateParent, delayed_tags):
            return        
        code = self.codeGenerator.get_lit_basic_code(event)
        self.codestack.append([self.callStack.getLength(), 'lit-tag', code])

        # other misc tasks
        self.__check_for_special_mode()
    
    def handle_var_start(self, event):
        #if True in map(self.compiler.callStack.hasEventNamed, delayed_tags):
        if True in map(self.compiler.callStack.hasImmediateParent, delayed_tags):
            return
        if self.compiler.callStack.hasImmediateParent('tag'):
            code = self.codeGenerator.get_var_basic_code(event, True)
        else:
            code = self.codeGenerator.get_var_basic_code(event)
        self.codestack.append([self.callStack.getLength(), 'var', code])
        
    def handle_append_start(self, event):
        global DEBUG_MODE        
        self.compiler.APPEND_MODE = True
        code = []
        if DEBUG_MODE:
            code.append(u'### DEBUG: ' + self.codeGenerator.get_xml_tag(event))
        code.append(u'push\t' +  event.attrs['n'])
        self.codestack.append([self.callStack.getLength(), 'append', code])
        
    def handle_let_start(self, event):
        global DEBUG_MODE
        code = []
        if DEBUG_MODE:
            code.append(u'### DEBUG: ' + self.codeGenerator.get_xml_tag(event))

    def handle_concat_start(self, event):
        global DEBUG_MODE
        self.compiler.CONCAT_MODE = True
        code = []
        if DEBUG_MODE:
            code.append(u'### DEBUG: ' + self.codeGenerator.get_xml_tag(event))
        self.codestack.append([self.callStack.getLength(), 'concat', code])
        
    def handle_list_start(self, event):
        global DEBUG_MODE
        code = []
        if DEBUG_MODE:
            code.append(u'### DEBUG: ' + self.codeGenerator.get_xml_tag(event))
        
        in_tag = self.callStack.getTop(2)
        if 'caseless' in in_tag.attrs and in_tag.attrs['caseless'] == 'yes':
            code.append(u'incini\t' + event.attrs['n'])
        else:
            code.append(u'incin\t' + event.attrs['n'])
        self.codestack.append([self.callStack.getLength(), 'list', code])
        
    def handle_pattern_item_start(self, event):
        self.compiler.pattern_item_count += 1
        
    def handle_chunk_start(self, event):
        code = []
        self.compiler.chunkModeArgs = 1
        
        if DEBUG_MODE:
            code.append(u'### DEBUG: ' + self.codeGenerator.get_xml_tag(event))
            
        #code.append('^')
        
        if u'name' in event.attrs:
            code.append('push\t"' + event.attrs['name'] + '"')
        elif u'namefrom' in event.attrs:
            code.append('pushv\t"' + event.attrs['namefrom'] + '"')
            
        self.codestack.append([self.callStack.getLength(), 'chunk', code])
        
    def handle_lu_start(self, event):
        #code = []
        #code.append('{^')
        #self.codestack.append([self.callStack.getLength(), 'lu', code])
        pass
    
    # code for <b/> and <b pos="X"/>
    def handle_b_start(self, event):
        code = []
        if 'pos' in event.attrs:
            code.append(u'pushsb\t' + event.attrs['pos'])
        else:
            code.append(u'pushbl')
        self.codestack.append([self.callStack.getLength(), 'b', code])
        
    # these are palceholder codes for now
    
    # code for modify-case
    def handle_modify_case_start(self, event):
        global DEBUG_MODE        
        code = []
        if DEBUG_MODE:
            code.append(u'### DEBUG: ' + self.codeGenerator.get_xml_tag(event))
        self.codestack.append([self.callStack.getLength(), event.name, code])
        
    def handle_case_of_start(self, event):
        global DEBUG_MODE        
        code = []
        if DEBUG_MODE:
            code.append(u'### DEBUG: ' + self.codeGenerator.get_xml_tag(event))
        self.codestack.append([self.callStack.getLength(), event.name, code])

    def handle_begins_with_start(self, event):
        global DEBUG_MODE        
        code = []
        if DEBUG_MODE:
            code.append(u'### DEBUG: ' + self.codeGenerator.get_xml_tag(event))
        self.codestack.append([self.callStack.getLength(), event.name, code])
        
    def handle_ends_with_start(self, event):
        global DEBUG_MODE        
        code = []
        if DEBUG_MODE:
            code.append(u'### DEBUG: ' + self.codeGenerator.get_xml_tag(event))
        self.codestack.append([self.callStack.getLength(), event.name, code])
        
    def handle_contains_substring_start(self, event):
        global DEBUG_MODE        
        code = []
        if DEBUG_MODE:
            code.append(u'### DEBUG: ' + self.codeGenerator.get_xml_tag(event))
        self.codestack.append([self.callStack.getLength(), event.name, code])
        
    def handle_get_case_from_start(self, event):
        global DEBUG_MODE        
        code = []
        if DEBUG_MODE:
            code.append(u'### DEBUG: ' + self.codeGenerator.get_xml_tag(event))
        self.codestack.append([self.callStack.getLength(), event.name, code])

    
    # list of 'ending' event handlers
    def handle_and_end(self, event, codebuffer):
        codebuffer.append(u'and')

    def handle_or_end(self, event, codebuffer):
        codebuffer.append(u'or')

    def handle_not_end(self, event, codebuffer):
        codebuffer.append(u'not')

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
    
    def handle_section_def_macros_end(self, event, codebuffer):
        label = u'section_def_macros_end'
        self.labels.append(label)
        codebuffer.append(label + ':\tnop')
        
    def handle_section_rules_end(self, event, codebuffer):
        # first get all the 'action'  tag 'lazy' codes from lazyBuffer
        tmpbuffer = []
        newLazyBuffer = []
        for name, code in self.compiler.lazyBuffer:
            if name == 'action':
                tmpbuffer.extend(code)
            else:
                # add the not matching code in newLazyBuffer
                newLazyBuffer.append([name, code])
                
        # finally add this tmpbuffer into codebuffer
        codebuffer.extend(tmpbuffer)
        # update compiler's lazyBuffer
        self.compiler.lazyBuffer = newLazyBuffer
        
        # code for this tag
        label = u'section_rules_end'
        self.labels.append(label)
        codebuffer.append(label + ':\tnop')

    def handle_def_macro_end(self, event, codebuffer):
        label = u'macro_' + event.attrs['n'] + u'_end'
        codebuffer.append(label + '\t:ret')
        self.labels.append(label)
        self.macroMode = False

    def handle_choose_end(self, event, codebuffer):
        childs = self.compiler.symbolTable.getChilds(event)
        ## pprint(childs)
        ## pprint(codebuffer)
        ## print

        has_otherwise = False
        for child in reversed(childs):
            if child.name == 'otherwise':
                has_otherwise = True
                break
        
        # reversing does not take much CPU time, so this is the preferred 
        # method over iterating in reverse
        if has_otherwise:
            codebuffer.reverse()
            for index, line in enumerate(codebuffer):
                if line.startswith('#!#jmp\t'):
                    codebuffer[index] = line.replace('#!#jmp\t', 'jmp\t')
                    break
            codebuffer.reverse()
            
    def handle_action_end(self, event, codebuffer):
        start_label = u'action_' + str(self.compiler.actionid) + u'_start'
        self.labels.append(start_label)
        codebuffer.insert(0, start_label + ':\tnop')
        
        end_label = u'action_' + str(self.compiler.actionid) + '_end'
        codebuffer.append(end_label + ':\tnop')
        
        # returning invokes the lazy buffer write
        return codebuffer
                
    def handle_when_end(self, event, codebuffer):
        code = []
        
        local_whenid = self.compiler.whenStack[-1]
        otherwise_end_label = u'otherwise_' + str(local_whenid)  + u'_end'
        when_end_label = u'when_' + str(local_whenid) + u'_end'
        
        self.labels.append(when_end_label)

        code.append('#!#jmp\t' + otherwise_end_label)
        code.append(when_end_label + ':\tnop')
        codebuffer.extend(code)
        
        #self.compiler.whenid += 1

        # set the otherwiseid, if there is actually any otherwise following this when
        # the otherwiseid will be used
        self.compiler.otherwiseid = local_whenid
        self.compiler.whenStack.pop()

    def handle_otherwise_end(self, event, codebuffer):
        label = u'otherwise_' + str(self.compiler.otherwiseStack[-1]) + u'_end'
        
        self.labels.append(label)
        codebuffer.append(label + ':\tnop')
        
        self.compiler.otherwiseStack.pop()

    def handle_test_end(self, event, codebuffer):
        # FIXME: this will probably not work in case of nested 'when' and 'otehrwise'
        # need to find something more mature
        codebuffer.append(u'jnz	when_' + str(self.compiler.whenStack[-1]) + '_end')

    # the followings are delayed mode tags
    def handle_let_end(self, event, codebuffer):
        #child1, child2 = self.compiler.parentRecord.getChilds(event)
        # EXPERIMENTAL
        child1, child2 =  self.compiler.symbolTable.getChilds(event)
        code = []
        if child1.name == 'clip':
            code = self.codeGenerator.get_clip_tag_basic_code(child1)
            if child2.name == 'lit-tag':
                code.extend(self.codeGenerator.get_lit_tag_basic_code(child2))
            elif child2.name == 'lit':
                code.extend(self.codeGenerator.get_lit_basic_code(child2))
            elif child2.name == 'var':
                code.extend(self.codeGenerator.get_var_basic_code(child2))
            elif child2.name == 'clip':
                code.extend(self.codeGenerator.get_clip_tag_basic_code(child2))
                # normal rvalue cliptl or clipsl for 'clip'
                code.extend(self.codeGenerator.get_clip_tag_rvalue_code(child2))
            elif child2.name == 'concat':
                idx = zip(*self.compiler.lazyBuffer)[0].index('concat')
                lazyCode = self.compiler.lazyBuffer.pop(idx)[1]
                code.extend(lazyCode)    

            # storetl or storesl
            code.extend(self.codeGenerator.get_clip_tag_lvalue_code(child1))

        if child1.name == 'var':
            # 'var' here is lvalue, so need special care
            code.append('push\t' + child1.attrs['n'])
            if child2.name == 'clip':
                code.extend(self.codeGenerator.get_clip_tag_basic_code(child2))
                # normal rvalue cliptl or clipsl for 'clip'
                code.extend(self.codeGenerator.get_clip_tag_rvalue_code(child2))
            elif child2.name == 'lit-tag':
                code.extend(self.codeGenerator.get_lit_tag_basic_code(child2))
            elif child2.name == 'lit':
                code.extend(self.codeGenerator.get_lit_basic_code(child2))
            elif child2.name == 'var':
                code.extend(self.codeGenerator.get_var_basic_code(child2))
            elif child2.name == 'concat':
                idx = zip(*self.compiler.lazyBuffer)[0].index('concat')
                lazyCode = self.compiler.lazyBuffer.pop(idx)[1]
                code.extend(lazyCode)

            # now the extra instuction for the assignment
            code.append(u'storev')
            
        codebuffer.extend(code)

    def handle_append_end(self, event, codebuffer):
        
        codebuffer.append(u'push\t' + str(self.compiler.appendModeArgs))
        codebuffer.append(u'appendv')

        # reset the state variables regarding append mode
        self.compiler.appendModeArgs = 0
        self.compiler.APPEND_MODE = False

    def handle_concat_end(self, event, codebuffer):
        # first append the required instruction to codebuffer
        codebuffer.append(u'push\t' + str(self.compiler.concatModeArgs))
        codebuffer.append(u'concat')
        
        # reset the state variables regarding append mode
        self.compiler.concatModeArgs = 0
        self.compiler.CONCAT_MODE = False

        # the caller function will check if this, and delay the codebuffer write
        return codebuffer
    
    def handle_pattern_end(self, event, codebuffer):
        childs = self.compiler.symbolTable.getChilds(event)
        code = []
        args = []
        
        # combination code
        #for child in childs:
        #    def_cat_id = child.attrs['n']
        #    args.append(self.compiler.def_cats[def_cat_id])
        #    
        #pattern_combinations = self.__cross(args)
        #for combination in pattern_combinations:
        #    for item in combination:
        #        code.append(u'push\t"' + item + '"')
        #    code.append(u'push\t' + str(self.compiler.pattern_item_count))
        #    
        #    # need to add 1 to actionid because we haven't reached the action yet
        #    code.append(u'addtrie\t"action_' + str(self.compiler.actionid + 1) + '_start"')
        
        # code without combination, for the time being work with this one
        for child in childs:
            def_cat_id = child.attrs['n']
            cat_items = self.compiler.def_cats[def_cat_id]
            regex = reduce(lambda x, y: x + u'|' + y, cat_items)
            #code.append(u'push\t"' + child.attrs['n'] + '"')
            code.append(u'push\t"' + regex + '"')
        code.append(u'push\t' + str(self.compiler.pattern_item_count))
        code.append(u'addtrie\t"action_' + str(self.compiler.actionid + 1) + '_start"')
            
        codebuffer.extend(code)
        self.compiler.pattern_item_count = 0
        #print code
        #print
        
    def handle_call_macro_end(self, event, codebuffer):        
        code = []
        childs = self.compiler.symbolTable.getChilds(event)
        # all the childs are <with-param> tag
        for child in childs:
            code.append(u'push\t' + child.attrs['pos'])
        code.append(u'push\t' + str(self.compiler.macro_args_count))
        code.append(u'call\tmacro_' + event.attrs['n'] + u'_start')
        
        codebuffer.extend(code)
        self.compiler.macro_args_count = 0
        
    def handle_chunk_end(self, event, codebuffer):
        childs = self.compiler.symbolTable.getChilds(event)
        
        no_of_brace_params = 0
        for child in childs:
            if child.name in ['lu', 'mlu', 'b']:
            #if child.name == 'lu' or child.name == 'mlu' or child.name == 'b':
                no_of_brace_params += 1
        
        code = []
        
        # put a brace around the curret lu/mlu collection
        code.append(u'brace\t' + str(no_of_brace_params))
        
        # varying version of chunk depending on 'case'
        # FIXE: are there more values for 'case' other than this 3?
        
        try:
            if event.attrs['case'] == 'caseFirstWord':
                code.append(u'chunkfw\t' + str(self.compiler.chunkModeArgs + 1))
            elif event.attrs['case'] == 'caseOtherWord':
                code.append(u'chunkow\t' + str(self.compiler.chunkModeArgs + 1))
            elif event.attrs['case'] == 'variableCase':
                code.append(u'chunkvc\t' + str(self.compiler.chunkModeArgs + 1))
        except KeyError:
            # if no data about the case of given, chunkfw is the default one
            code.append(u'chunkfw\t' + str(self.compiler.chunkModeArgs + 1))
            
        codebuffer.extend(code)
        
        
    def handle_lu_end(self, event, codebuffer):
        childs = self.compiler.symbolTable.getChilds(event)
        no_of_lu_params = len(childs)
        code = []
        code.append(u'lu\t' + str(no_of_lu_params))
        codebuffer.extend(code)
        
    def handle_mlu_end(self, event, codebuffer):
        childs = self.compiler.symbolTable.getChilds(event)
        no_of_mlu_params = len(childs)
        code = []
        code.append(u'mlu\t' + str(no_of_mlu_params))
        codebuffer.extend(code)
        
    def handle_out_end(self, event, codebuffer):
        childs = self.compiler.symbolTable.getChilds(event)
        no_of_out_params = len(childs)
        code = []
        code.append(u'out\t' + str(no_of_out_params))
        codebuffer.extend(code)
        
    def handle_tag_end(self, event, codebuffer):
        self.compiler.chunkModeArgs += 1

    def handle_modify_case_end(self, event, codebuffer):
        first, second = self.compiler.symbolTable.getChilds(event)
        
    def handle_transfer_end(self, event, codebuffer):
        # finally, the hlt instruction
        codebuffer.append(u'hlt')