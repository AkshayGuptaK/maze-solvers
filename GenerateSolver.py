'''Matrix based Maze Solvers'''
#Solver Generator

import numpy as np
import random

def print_multi_nparray(multi_array): #output display function
    layers = multi_array.shape[-1]
    for layer in range(layers):
        print(multi_array[..., layer])

class MemorySolver():
    #class of solvers that always try the same path - they can be evolved to better solve a given maze
    def __init__(self, maze):
        self.genome = np.copy(maze)
        self.end = self.genome.shape[0] - 1
        
    def construct(self, random):
        #initializes this solver's path - i.e. its attempted solution
        i = 0
        j = 0
        end_reached = False
        self.path = []
        
        while j not in self.path:
            self.path.append(j)
            if j == self.end:
                end_reached = True
            j = random.choice(np.where(self.genome[i,:]==1)[0].tolist()) #choose a random path not previously chosen
            self.genome[i, j] = 2 #marks this as a path taken in the genome
            i = j
            if end_reached:
                break
                        
        for i in [x for x in range(1, self.end+1) if x not in self.path]:
            j = random.choice(np.where(self.genome[i,:]==1)[0].tolist())
            self.genome[i, j] = 2
            #paths are added so all nodes are traversed at least once by solution
            
    def gen_path(self):
        #traces the path indicated by the genome
        #this is for post evolutionary use in determining the new solution
        i = 0
        j = 0
        end_reached = False
        self.path = []
        
        while j not in self.path:
            self.path.append(j)
            if j == self.end:
                end_reached = True
            (j, ) = np.where(self.genome[i,:]==2)[0]
            i = j
            if end_reached:
                break        
            
def generate_memory_solver(random, args):
    solver = MemorySolver(args.get('maze'))
    solver.construct(random)
    return solver
    
def evaluate_memory_solver(candidates, args):
    fitness = []
    
    for solver in candidates:
        try:
            fitness.append(solver.path.index(solver.end)) #num of steps taken to solve
        except ValueError: #if solver cannot solve the maze
            fitness.append(solver.end + 1)
        
    return fitness    

#------------------------------------------------------------------------------    
    
def generate_smart_solver(random, args):
    #solvers that use a 3d matrix to generate a solution given a certain maze or set of mazes
    #can be evolved to produce a genetic 'algorithm' which can solve mazes in general
    nodes = args.get('nodes') #number of nodes in the maze
    complexity = args.get('complexity') #determines number of layers (third dimension size) of solver matrix

    solver = np.ones((nodes, nodes, complexity), np.int8)
    
    for layer in range(1, complexity):
        for row in range(nodes):
            solver[row, :, layer] = [random.randint(0,3) for i in range(nodes)]
    #initializes random values between 0 and 3 for all layers except bottom layer
    return solver

def identity_solver(nodes, complexity):
    #random but prefers not to revisit nodes - for performance comparison purposes
    solver = np.zeros((nodes, nodes, complexity), np.int8)

    for i in range(nodes):
        solver[i, i, -1] = 1
        
    solver[:, :, 0] = 1
    
    return solver
    
def dfs_solver(nodes, complexity):
    #a basic implementation of a depth first search solver - for performance comparison
    solver = np.ones((nodes, nodes, complexity), np.int8)
    
    solver[:, :, -1] = 2

    for i in range(nodes):
        solver[i, i, -1] = 1
    return solver
    
def optimal_solver(nodes):
    #believed to be optimal solving strategy - for performance comparison
    solver = np.ones((nodes, nodes, 3), np.int8)
    
    solver[:, :, -1] = 0
    
    for i in range(nodes):
        solver[i, i, -1] = 1

    solver[:, :, -2] = 2
    
    return solver
    
def visit(node, unvisited, tensor): #mark a node as visited
    unvisited[node] = 0
    tensor[node, :] = 1
    tensor[:, node] = 1
    
def operate(number, operator): #performs the operation specified by the solver matrix
    if operator == 0 or operator == 1: #a 0 or 1 operator returns itself as the result
        return operator
    elif operator == 2: #a 2 operator returns the number operated on without change
        return number
    else: #a 3 operator returns the inverse of the number operated on
        return 1 - number
    
def matrix_operate(matrix, operator): 
    #performs row and column wise operations between number matrix and operator matrix
    result = np.zeros(matrix.shape, np.int8)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            result[i, j] = operate(matrix[i, j], operator[i, j])
    return result

def choose(random, row): #choose at random between possible options, if multiples
    if np.count_nonzero(row):
        return random.choices([n for n in range(row.shape[0])], weights=row)
    else:
        return (-1, )
        
def evaluate_smart_solver(candidates, args): #mazes is a numpy array of node x node x number_of_mazes
    random = args.get('random')
    mazes = args.get('mazes')

    fitness = [] #will store the success value for solving attempt on each maze
    nodes = mazes.shape[0] #number of nodes in the maze
    
    for solver in candidates:
        fit = 0
        for maze in range(mazes.shape[2]):
            unvisited = [1 for x in range(nodes)] #list of 1s in place of each unvisited node, 0s for each visited node
            tensor = np.zeros((nodes, nodes), np.int8)
            current = 0 #current node initialized to beginning node of maze
            steps = 0 #number of moves made so far
            visit(0, unvisited, tensor)
            
            while current != nodes - 1 and steps < nodes**2:
                choice = -1
                layer = -1
                known = np.multiply(tensor, mazes[:, :, maze]) #yields the information of maze adjacency as known by solver at current time
            
                while choice < 0:
                    try:
                        M = matrix_operate(known, solver[:, :, layer]) #performs solver matrix operation to determine which path to take
                    except IndexError:
                        print('Index Error')
                        break
                    except TypeError:
                        print('Type Error')
                        print(solver)
                        break
                    result = np.multiply(np.dot(unvisited, M), mazes[current, :, maze]) #multiplication by maze adj matrix eliminates impossible choices
                    (choice,) = choose(random, result)
                    layer -= 1
                    
                current = choice
                steps += 1
                visit(choice, unvisited, tensor)
                
            fit += steps
        fitness.append(fit)
        
    return fitness
