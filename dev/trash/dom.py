from xml.dom.minidom import parseString
import codecs

def handle_def_cats(def_cats):
    for def_cat in def_cats:
        for attr in def_cat.attributes:
            attr
            

f = codecs.open('apertium-en-ca.en-ca.t1x', 'r', 'utf-8')
doc = parseString(f.read().encode('utf-8'))
def_cats = doc.getElementsByTagName('def-cat')
handle_def_cats(def_cats)

print 'OK'
