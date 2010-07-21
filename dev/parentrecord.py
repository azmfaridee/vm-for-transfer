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
