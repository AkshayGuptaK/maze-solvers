'''Conducts an evolutionary computation to develop better solvers'''

from random import Random
from time import time
from inspyred import ec
from GenerateMaze import *
from GenerateSolver import *
from MicroEC import *

def discard_useless(random, population, args): #removes obviously suboptimal solvers
	return [x for x in population if x.fitness <= x.candidate.end]

def cross_memory_solver(random, mom, dad, args): #crosses two solvers to produce offspring
	child1 = MemorySolver(mom.genome)
	child2 = MemorySolver(dad.genome)
		
	intersect = [x for x in mom.path if x in dad.path]
	dad_only = [x for x in dad.path if x not in intersect]
	mom_only = [x for x in mom.path if x not in intersect]
	
	for i in dad_only:
		child1.genome[i, :] = dad.genome[i, :]
	
	for j in mom_only:
		child2.genome[j, :] = mom.genome[j, :]

	c = [mom, dad]
	
	for k in intersect:
		random.shuffle(c)
		child1.genome[k, :] = c[0].genome[k, :]
		child2.genome[k, :] = c[1].genome[k, :]
							
	return (child1, child2)

def mutate_memory_solver(random, candidate, args): #random mutation
	row = random.randint(0, candidate.end)
	(old_column, ) = np.where(candidate.genome[row, :]==2)[0]
	candidate.genome[row, old_column] = 1
	new_column = random.choice(np.where(candidate.genome[row,:]==1)[0].tolist())
	candidate.genome[row, new_column] = 2
	return candidate
	
def variate_memory_solver(random, candidates, args): #performs the generational variation process
	children = ec.variators.crossover(cross_memory_solver)(random, candidates, args)
	mutants = ec.variators.mutator(mutate_memory_solver)(random, children, args)
	for mutant in mutants:
		mutant.gen_path()
	return mutants

def test_observer(population, num_generations, num_evaluations, args): #display function
	print('Generation ' + str(num_generations))
	for individual in population:
		print('Candidate')
		print(individual.candidate.genome)
		print(individual.fitness)

def evolve_memory_solvers(nodes, paths, solvers, sel_pressure, generations, maze_function=generate_simple_maze): 
    #performs evolutionary computuation for memory solvers		
	rand = Random()
	rand.seed(int(time()))
	computation = ec.EvolutionaryComputation(rand)
	computation.terminator = ec.terminators.generation_termination
	computation.selector = ec.selectors.rank_selection #could use rank or truncation or discard_useless
	computation.variator = variate_memory_solver #could use default ec.variators.default_variation
	computation.replacer = ec.replacers.truncation_replacement #could use steady_state
	computation.observer = ec.observers.stats_observer #could use test_observer
	#migrator is default for now
	#archiver is default for now
	gen_maze = maze_function(rand, nodes, paths)

	return computation.evolve(generate_memory_solver, evaluate_memory_solver, pop_size=solvers, maximize=False, maze=gen_maze, num_selected=sel_pressure, max_generations=generations)

#An example run:
#result = evolve_memory_solvers(20, 15, 1000, 500, 20)
#best_candidate = result[0].candidate
#print_multi_nparray(best_candidate.genome)
#print(result[0].fitness)

#########################################################

def cross_smart_solver(random, mom, dad, args): #cross two parent solvers to produce offspring

	child1 = np.copy(mom)
	child2 = np.copy(dad)
	parents = [mom, dad]
	
	for layer in range(1, mom.shape[2]):		
		random.shuffle(parents)
		child1[:, :, layer] = parents[0][:, :, layer]
		child2[:, :, layer] = parents[1][:, :, layer]	
							
	return (child1, child2)
	
def mutate_smart_solver(random, candidate, args): #random mutation
	mutations = args.get('mutations')
	
	for i in range(mutations):
		row = random.randint(0, candidate.shape[0]-1)
		column = random.randint(0, candidate.shape[1]-1)
		layer = random.randint(1, candidate.shape[2]-1)
		candidate[row, column, layer] = random.randint(0,3)
	return candidate
	
def variate_smart_solver(random, candidates, args): #performs generational variation
	children = ec.variators.crossover(cross_smart_solver)(random, candidates, args)
	mutants = ec.variators.mutator(mutate_smart_solver)(random, children, args)
	return mutants

def evolve_smart_solvers(mazes, nodes, paths, solvers, sel_pressure, generations, complexity, mutations, maze_function=generate_simple_maze):		
    #performs evolutionary computation for smart solvers
	rand = Random()
	rand.seed(int(time()))
	computation = ec.EvolutionaryComputation(rand)
	computation.terminator = ec.terminators.generation_termination
	computation.selector = ec.selectors.rank_selection #could use rank or truncation or discard_useless
	computation.variator = variate_smart_solver #ec.variators.default_variation
	computation.replacer = ec.replacers.truncation_replacement #could use steady_state
	computation.observer = ec.observers.stats_observer #could use test_observer
	#migrator is default for now
	#archiver is default for now
	maze_set = generate_mazes(rand, maze_function, mazes, nodes, paths)

	return (computation.evolve(generate_smart_solver, evaluate_smart_solver, pop_size=solvers, maximize=False, num_selected=sel_pressure, max_generations=generations, nodes=nodes, complexity=complexity, random=rand, mazes=maze_set, mutations=mutations), maze_set)

def evaluate_mazes(mazes, nodes):
    #evaluates mazes using preset solvers for performance comparison purposes
    args = {'random': Random(), 'mazes': mazes}
    identity = identity_solver(nodes, 2)
    dfs = dfs_solver(nodes, 2)
    optimal = optimal_solver(nodes)
    print('Identity does it in ')
    print(evaluate_smart_solver([identity], args))
    print('DFS does it in ')
    print(evaluate_smart_solver([dfs], args))
    print('Optimal does it in')
    print(evaluate_smart_solver([optimal], args))

#An example run:
#result, mazes = evolve_smart_solvers(mazes=5, nodes=10, paths=10, solvers=100, sel_pressure=50, generations=5, complexity=3, mutations=20)
#evaluate_mazes(mazes, 10)
#best_candidate = result[0].candidate
#print_multi_nparray(best_candidate)
#print(result[0].fitness)