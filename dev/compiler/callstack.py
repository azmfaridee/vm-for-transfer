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
