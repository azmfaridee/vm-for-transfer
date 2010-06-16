from lxml import etree as ElementTree
import codecs

fname = 'apertium-en-ca.en-ca.t1x'

f = codecs.open(fname, 'r', 'utf-8')
s = f.read().encode('utf-8')

print "Running program"
#print s
#t = ElementTree.parse()
print "Program ended"
