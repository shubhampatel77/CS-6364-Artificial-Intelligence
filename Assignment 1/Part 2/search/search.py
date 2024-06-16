# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

from util import *

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]


class Node:
    
    """
    Custom node class for easy path return. Also keeps track of parent nodes 
    """
    
    def __init__(self, state, action=None, parent=None, cost=0):
        self.state = state
        self.action = action
        self.parent = parent
        self.cost = cost
    
    def getPath(self):
        path = []
        parent = self.parent
        action = self.action
        while parent and action:
            path.insert(0, action)
            action = parent.action
            parent = parent.parent
        return path

def getFringe(search_strategy):
    
    """
    Returns a relevant data structure
    """
    fringes = {
        'dfs': Stack(),
        'bfs': Queue(),
        'ucs': PriorityQueueWithFunction(lambda x: x.cost),
    }

    return fringes.get(search_strategy)

def searchAlgorithm(search_strategy, problem):
    """
        searchStrategy: An abbreviated string which specifies the search strategy
        heurestic: passed as None for uninformed search, otherwise a well-defined heurestic
        
    Returns the path (sequence of actions) to reach a goal state, given initial conditions
    """
    L = getFringe(search_strategy)
    
    start_node = Node(problem.getStartState(), None, None, 0)

    L.push(start_node)
    visited = set()

    while not L.isEmpty():
        current_node = L.pop()
        current_state = current_node.state

        if problem.isGoalState(current_state):
            return current_node.getPath()

        if current_state not in visited:
            visited.add(current_state)
            successors = problem.getSuccessors(current_state)
            for s in successors:
                L.push(Node(s[0], s[1], current_node, current_node.cost + s[2]))
    return []
    

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    "*** YOUR CODE HERE ***"
    
    return searchAlgorithm('dfs', problem)
           

def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    return searchAlgorithm('bfs', problem)

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    return searchAlgorithm('ucs', problem)

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

    

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    
    L = PriorityQueue()
    start_node = Node(problem.getStartState(), None, None, 0)
    L.push(start_node, start_node.cost + heuristic(start_node.state, problem))
    visited = set()
    
    while not L.isEmpty():
        current_node = L.pop()
        current_state = current_node.state
        
        if problem.isGoalState(current_state):
            return current_node.getPath()
        
        if current_state not in visited:
            visited.add(current_state)
            successors = problem.getSuccessors(current_state)
            for s in successors:
                h = heuristic(s[0], problem)
                L.push(Node(s[0], s[1], current_node, current_node.cost + s[2]), current_node.cost + s[2] + h)
                
    return []

# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
