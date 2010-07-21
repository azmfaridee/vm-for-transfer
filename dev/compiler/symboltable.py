class SymbolTable(object):
    def __init__(self, callStack):
        self.symbolList = {}
        self.childList = {}

        self.currentSymbolId = 0

        self.callStack = callStack

    def addSymbol(self, event):
        # symbol id starts from 1
        self.currentSymbolId += 1        
        self.symbolList[self.currentSymbolId] = event

        currentParentId = -1
        try: currentParent = self.callStack.getTop(2)
        except: currentParent = None
        currentParentId = self.__getId(currentParent)

        if currentParentId not in self.childList.keys():
            self.childList[currentParentId] = []
        self.childList[currentParentId].append(self.currentSymbolId)

    def __getId(self, event):
        eventId = -1
        # this is only for safety, most of the time eventId would be
        # equal to currentSymbolId
        for i in range(self.currentSymbolId, 0, -1):
            if self.symbolList[i] == event:
                return i
        return eventId
            

    def getChilds(self, event):
        eventId = self.__getId(event)
        ## print event
        ## print eventId
        ## pprint(self.childList)
        ## pprint(self.symbolList)
        ## print self.symbolList[719]
        childs = []
        for childId in self.childList[eventId]:
            childs.append(self.symbolList[childId])
        return childs
        
