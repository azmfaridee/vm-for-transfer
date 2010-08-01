from copy import copy, deepcopy
DEBUG_MODE = True

class CodeGenerator(object):
    def __init__(self, compiler):
        self.compiler = compiler
    
    def get_xml_tag(self, event):
        tag = '<' + event.name
        for attr in event.attrs.keys():
            tag +=  ' ' + attr + '="' + event.attrs[attr] + '"'
        tag += '/>'
        return tag

    # code generators
    def get_lit_tag_basic_code(self, event):
        global DEBUG_MODE
        code = []
        if DEBUG_MODE:
            code.append(u'### DEBUG: ' + self.get_xml_tag(event))
        code.append(u'push\t"<' + event.attrs['v'] + '>"')        
        return code

    def get_clip_tag_basic_code(self, event):
        global DEBUG_MODE        
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
            code.append(u'### DEBUG: ' + self.get_xml_tag(event))
        # push pos
        code.append(u'push\t' + event.attrs['pos'])
        # push regex
        code.append(u'push\t"' + regex + u'"')

        return code

    def get_clip_tag_lvalue_code(self, event):
        # rvalue code, we want to 'write' new value into clip
        code = []
        if event.attrs['side'] == 'sl': code.append(u'storesl')
        elif event.attrs['side'] == 'tl': code.append(u'storetl')
        return code

    def get_clip_tag_rvalue_code(self, event):
        # rvalue code, we want to 'read' clip's value
        code = []
        if event.attrs['side'] == 'sl': code.append(u'clipsl')
        elif event.attrs['side'] == 'tl': code.append(u'cliptl')
        return code

    def get_lit_basic_code(self, event):
        global DEBUG_MODE        
        # FIXME: fix the problem with empty lit e.g. <lit v=""/>
        # print 'DEBUG push', event.attrs['v'].encode('utf-8')
        code = []
        if DEBUG_MODE:
            code.append(u'### DEBUG: ' + self.get_xml_tag(event))        
        code.append(u'push\t"' + event.attrs['v'] + '"')
        return code    

    def get_var_basic_code(self, event):
        global DEBUG_MODE        
        code = []
        if DEBUG_MODE:
            code.append(u'### DEBUG: ' + self.get_xml_tag(event))                
        code.append(u'pushv\t"' + event.attrs['n'] + '"')
        return code
 
    def get_pattern_basic_code(self, event):
        pass