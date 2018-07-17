'''Single run evaluation of given solver on given maze'''

from random import Random
from time import time
from GenerateMaze import *
from GenerateSolver import *

def evaluate_solver(solver, maze, random):
	nodes = maze.shape[0] #number of nodes in the maze
	
	unvisited = [1 for x in range(nodes)] #list of 1s in place of each unvisited node, 0s for each visited node
	tensor = np.zeros((nodes, nodes), np.int8)
	current = 0 #current node initialized to beginning node of maze
	steps = 0 #number of moves made so far
	visit(0, unvisited, tensor)
			
	while current != nodes - 1 and steps < nodes**2:
		choice = -1
		layer = -1
		known = np.multiply(tensor, maze) #yields the information of maze adjacency as known by solver at current time
			
		while choice < 0:
			try:
				M = matrix_operate(known, solver[:, :, layer]) #performs solver matrix operation to determine which path to take
			except IndexError:
				print('Index Error')
				break
			result = np.multiply(np.dot(unvisited, M), maze[current, :]) #multiplication by maze adj matrix eliminates impossible choices
			(choice,) = choose(random, result)
			layer -= 1
					
		current = choice
		steps += 1
		visit(choice, unvisited, tensor)
						
	return steps

def do_test(nodes, paths, complexity, maze_function=generate_simple_maze, solver_function=identity_solver):    
    rand = Random()
    rand.seed(int(time()))

    maze = maze_function(rand, nodes, paths)
    solver = solver_function(nodes, complexity)
    print(evaluate_solver(solver, maze, rand))

    print_multi_nparray(maze)

do_test(10, 15, 2)