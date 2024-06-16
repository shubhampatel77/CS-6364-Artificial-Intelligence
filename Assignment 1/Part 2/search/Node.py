class Node:
    def __init__(self, state, action=None, parent=None, cost=0, h=0):
        self.state = state
        self.action = action
        self.parent = parent
        self.cost = cost
        self.h = h
    
    def getPath(self):
        path = []
        parent = self.parent
        action = self.action
        while parent and action:
            path.insert(0, action)
            action = parent.action
            parent = parent.parent
        return path
