class Event(object):
    def __init__(self, name, attrs):
        self.name = name
        self.attrs = attrs

    def __eq__(self, other):
        if other == None:
            return False
        if self.name == other.name and self.attrs == other.attrs:
            return True
        return False

    def __repr__(self):
        return vars(self).__str__()

    def __genid(self):
        pass
