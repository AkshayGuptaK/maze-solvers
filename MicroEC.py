import collections
import inspyred

class MicroEC(inspyred.ec.EvolutionaryComputation):
    def __init__(self, random):
        inspyred.ec.EvolutionaryComputation.__init__(self, random)
        
    def evolve(self, generator, evaluator, pop_size=10, seeds=None, maximize=True, bounder=None, **args):
        self._kwargs = args
        self._kwargs['_ec'] = self
        
        if seeds is None:
            seeds = []
        if bounder is None:
            bounder = inspyred.ec.Bounder()
        
        self.termination_cause = None
        self.generator = generator
        self.evaluator = evaluator
        self.bounder = bounder
        self.maximize = maximize
        self.population = []
        self.archive = []
        microseeds = seeds
        
        while not self._should_terminate(list(self.population), self.num_generations, self.num_evaluations):
            microec = inspyred.ec.EvolutionaryComputation(self._random)
            microec.selector = self.selector
            microec.variator = self.variator
            microec.replacer = self.replacer
            microec.observer = self.observer
            microec.terminator = inspyred.ec.terminators.evaluation_termination
            maxevals = args['max_evaluations']
            args['max_evaluations'] = args['micro_evaluations']
            result = microec.evolve(generator=generator, evaluator=evaluator, 
                                    pop_size=pop_size, seeds=microseeds, 
                                    maximize=maximize, **args)
            self.population = list(result)
            args['max_evaluations'] = maxevals
            result.sort(reverse=True)
            microseeds = [result[0].candidate]
            self.num_evaluations += microec.num_evaluations

            # Migrate individuals.
            self.population = self.migrator(random=self._random, 
                                            population=self.population, 
                                            args=self._kwargs)
            
            # Archive individuals.
            self.archive = self.archiver(random=self._random, archive=self.archive, 
                                         population=list(self.population), args=self._kwargs)
            
            self.num_generations += microec.num_generations
            if isinstance(self.observer, collections.Iterable):
                for obs in self.observer:
                    obs(population=list(self.population), num_generations=self.num_generations, 
                        num_evaluations=self.num_evaluations, args=self._kwargs)
            else:
                self.observer(population=list(self.population), num_generations=self.num_generations, 
                              num_evaluations=self.num_evaluations, args=self._kwargs)
        return self.population

#Obtained from Inspyred Github Recipes page