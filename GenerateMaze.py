"""Creates mazes in the form of adjacency matrixes"""

#Maze Generator

import numpy as np
import random

def add_path(node1, node2, maze, p): #adds a path between two nodes
	maze[node1, node2] = 1
	maze[node2, node1] = 1
	return p + 1

def check_full(maze, node, nodes): #checks if more paths can be added for a given node
	return np.count_nonzero(maze, 1)[node] == nodes-1	
	
def fill_paths(random, maze, nodes, paths, maxpaths): 
    #adds additional paths up to specified maximum to the maze at random
	empty = {node for node in range(nodes-1) if not check_full(maze, node, nodes)}
	
	while paths < maxpaths:
		i = random.choice(tuple(empty))
		choices = np.where(maze[i,:]==0)[0].tolist()
		choices.remove(i)
		j = random.choice(choices)
		paths = add_path(i, j, maze, paths)
		if check_full(maze, i, nodes):
			empty.discard(i)
		if check_full(maze, j, nodes):
			empty.discard(j)		
	
def generate_simple_maze(random, nodes, paths):
    #random maze which biases degree in favor of nodes closer to entry
	maze = np.zeros((nodes, nodes), np.int8)
	i = 0
	traversed = {0}
	all_nodes = {node for node in range(nodes-1)}
	p = 0
	
	while all_nodes - traversed:
		j = random.choice(tuple(all_nodes-traversed))
		p = add_path(i, j, maze, p)
		traversed.add(j)
		i = random.choice(tuple(traversed))
		
	p = add_path(i, nodes-1, maze, p)
	
	fill_paths(random, maze, nodes, p, paths)
			
	return maze
	
def generate_tree_plus(random, degree_function, nodes, paths):
    #builds a tree like maze with specified degree for each node, plus additional random paths if desired
	tree = np.zeros((nodes, nodes), np.int8)
	paths = paths if paths else nodes-1
	i = 0
	built = {0}
	current_level = {0}
	all_nodes = {node for node in range(nodes-1)}
	p = 0
	link = 0
	
	while all_nodes - built:
		new_level = set()
		for i in current_level:
			for degree in range(degree_function(random)):
				if all_nodes - built:
					j = random.choice(tuple(all_nodes - built))
					p = add_path(i, j, tree, p)
					built.add(j)
					new_level.add(j)
				else:
					link = i
					break
		current_level = new_level
	
	link = link if link else random.choice(tuple(new_level))
	p = add_path(link, nodes-1, tree, p)	
		
	fill_paths(random, tree, nodes, p, paths)
	
	return tree	

def generate_helix_maze(random, nodes=6, forks=2, junctions=1, min_segment=0, max_segment=1): 
    # nodes > (junctions+1)((forks-1)*max_segment + min_segment)+junctions+2
	helix = np.zeros((nodes, nodes), np.int8)
	junction_rows = [random.randint(1, nodes-2) for x in range(junctions)]
	#complete this
	
def generate_mazes(random, maze_function, num_mazes=1, *args):
	mazes = []
	for i in range(num_mazes):
		mazes.append(maze_function(random, *args))
	return np.stack(mazes, axis=-1)
	
def make_constant(constant):
	return lambda random: constant
	
def make_randomizer(maxdegree):	
	return lambda random: random.randint(1, maxdegree)