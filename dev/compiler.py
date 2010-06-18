import xml.parsers.expat
import codecs
from pprint import pprint
import sys

DEBUG_MODE = False

# this stack holds information of the tree
stack = []
# genereated codes are held in the this stack and merged when necessary
codestack = []
# use this dictionary to keep track of current tags chindren
children = {}

def_cats = {}
def_attrs = {}
# generated regex from input def_attrs
def_attrs_regex = {}
def_lists = {}

# only these tags consist actual leafs
leaf_tags = ['clip', 'lit', 'lit-tag', 'with-param', 'var',  'b', 'list', 'pattern-item']

# these tags do not need processging for code generation
# more tags to clarify: transfer, section-rules
dec_tags = ['cat-item', 'def-cat', 'section-def-cats', 'attr-item', 'def-attr', 'section-def-attrs', 'def-var', 'list-item', 'def-list', 'section-def-vars', 'section-def-lists']

# longest common substring function
lcs = lambda a, b: lcs(a[:-1], b) if b.find(a) == -1 else a

def process_def_attrs():
    for def_attr in def_attrs.keys():
        # 
        def_attrs_regex[def_attr] = reduce(lambda x, y: x + '|' + y, def_attrs[def_attr])

        # FIXME: trying to do some optimization in regex
        # could do the same way as Jacob's attrItemRegexp function
        # though according to jacob, regex optimization does not help
        # that much
        
        ## common = reduce(lcs, def_attrs[def_attr])
        ## regex = common
        ## if len(def_attrs[def_attr]) > 1:
        ##     for x in def_attrs[def_attr]:
        ##         regex = regex + '(' + x[len(common):] + ')|'
        ## print regex[:-1]

# 3 handler functions
def start_element(name, attrs):
    stack.append([name, attrs])

    if name == 'cat-item':
        def_cat_id = stack[-2][1]['n']
        if def_cat_id not in def_cats:
            def_cats[def_cat_id] = []

        # lemma is OPTIONAL
        if 'lemma' in attrs.keys():
            regex = attrs['lemma']
        else:
            regex = '\w'

        # tags is REQUIRED, but still for safety we're checking
        if 'tags' in attrs.keys():
            tags = attrs['tags'].split('.')
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

        def_cats[def_cat_id].append(regex)
        
    if name == 'attr-item':
        def_attr_id = stack[-2][1]['n']
        
        if def_attr_id not in def_attrs:
            def_attrs[def_attr_id] = []
            
        #print def_attr_id, attrs
        tags = attrs['tags'].split('.')
        regex = ''
        for tag in tags:
            regex = regex + '<' + tag + '>'

        def_attrs[def_attr_id].append(regex)

    if name == 'list-item':
        def_list_id = stack[-2][1]['n']
        if def_list_id not in def_lists:
            def_lists[def_list_id] = []
            
        def_lists[def_list_id].append(attrs['v'])

    if name == 'def-macro':
        code = []
        
        macro_name = attrs['n']
        npar = int(attrs['npar'])

    if name == 'clip':
        codestack.append([len(stack), 'clip', handle_clip(name, attrs)])
    
    if name == 'lit-tag':
        codestack.append([len(stack), 'lit-tag', handle_lit_tag(name, attrs)])

def handle_lit_tag(name, attrs):
    code = []
    tag = '<' + attrs['v'] + '>'
    code.append('push\t' + tag)
    return code

def handle_clip(name, attrs):
    macro_mode = False
    store_mode = False
    
    for item in stack:
        if item[0] == 'def-macro':
            macro_mode = True
        if item[0] == 'let':
            store_mode = True

    code = []
    # FIXME: create code for lem, lemh, lemq, whole, tags
    if attrs['part'] not in ['lem', 'lemh', 'lemq', 'whole', 'tags']:
        # FIXME: has to come up with a better version of the regex
        regex = reduce(lambda x, y: x + '|' + y, def_attrs[attrs['part']])
        # push pos
        code.append('push\t' + attrs['pos'])
        # push regex
        code.append('push\t' + regex)
        if store_mode == False:
            if attrs['side'] == 'sl': code.append('clipsl')
            elif attrs['side'] == 'tl': code.append('cliptl')
    else:
        code.append('#DUMMY: lem, lemh, lemq, whole, tags')
#    print attrs['part'], code
    return code
    
def end_element(name):
    pitem = stack[-1]

    # skip the def-cat section, only def-macro and rules section
    if DEBUG_MODE == True and 'def-macro' in zip(*stack)[0]:
        print 'DEBUG IN: element', name, 'codestack', codestack
    
    # if this node is not a leaf as well as not from
    # declaration section
    if pitem[0] not in leaf_tags and pitem[0] not in dec_tags:
        depth = len(stack)
        #print pitem, len(stack), stack
        #print codestack
        code_buff = []

        # pop all the values from stack which have higher depth than
        # current depth, then add them to code_buff
        while len(codestack) > 0 and codestack[-1][0] > depth:
            # need to do a reverse, don't actually remember why now :(
            for statement in reversed(codestack[-1][2]):
                code_buff.insert(0, statement)
            # print codestack, code_buff
            codestack.pop(-1)

        # here comes all the condition section
        if name == 'and':
            pass
        if name == 'or':
            pass
        if name == 'not':
            pass
        if name == 'equal':
            # check if caseless
            try:
                if pitem[1]['caseless'] == 'yes':
                    code_buff.append('cmpi')
            except KeyError:
                code_buff.append('cmp')
        if name == 'begins-with':
            pass
        if name == 'ends-with':
            pass
        if name == 'contains-substring':
            pass
        if name == 'in':
            pass

        if name == 'let':
            #print 'DEBUG', code_buff
            pass

        code = []
        # merge code buff into a new code segment
        for x in code_buff:
            code.append(x)
        # insert this new code into code_stack
        codestack.append([depth, name, code])
        
    if DEBUG_MODE == True and 'def-macro' in zip(*stack)[0]:
        print 'DEBUG OUT: element', name, 'codestack', codestack
        print
    

    # pop the item from call stack
    stack.pop(-1)
    
def char_data(data):
    #print 'Character data:', repr(data)
    pass

if __name__  == '__main__':
    p = xml.parsers.expat.ParserCreate()

    p.StartElementHandler = start_element
    p.EndElementHandler = end_element
    p.CharacterDataHandler = char_data


#    f = codecs.open('apertium-en-ca.en-ca.t1x', 'r', 'utf-8')
    f = codecs.open('input-compiler/set2.t1x', 'r', 'utf-8')
    s = f.read()
    p.Parse(s.encode('utf-8'))

    #process_def_attrs()
    #print def_cats
    #print def_attrs
    #print def_lists
    pprint(codestack)
