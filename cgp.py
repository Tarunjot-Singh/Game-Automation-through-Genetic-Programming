#Cartesian Genetic Programming Main File

#Importing all the required libraries
import random
import copy
import operator as op
from settings import Verb, NODE_COLS, INPUT_CGP_LEVELS


class General_Function:
    # General Class Function for initialization
    def __init__(self, f, arg_operand):
        self.f = f
        self.arg_operand = arg_operand

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)


class Node_GCP_graph:
    # Node in the CGP graph
    def __init__(self, max_arg_operand):
        # Initializing the node randomly
        self.init_func = None
        self.init_inputs = [None] * max_arg_operand
        self.weights = [None] * max_arg_operand
        self.init_output = None
        self.output = None
        self.active = False


class Individual_Genetic_Program:
    # For individual evolution for the genetic program
    function_set = None
    # Adjusting the range of weights
    weight_range = [-1, 1]
    # Argument Operands
    max_arg_operand = 3
    
    number_of_inputs = 3
    number_of_outputs = 1
    node_cols = NODE_COLS
    INPUT_CGP_LEVELS = INPUT_CGP_LEVELS

    def __init__(self):
        self.nodes = []
        for pos in range(self.node_cols):
            self.nodes.append(self._create_random_node(pos))
        for i in range(1, self.number_of_outputs + 1):
            self.nodes[-i].active = True
        self.fitness = None
        self._active_determined = False

    def _create_random_node(self, pos):
        node = Node_GCP_graph(self.max_arg_operand)
        node.init_func = random.randint(0, len(self.function_set) - 1)
        for i in range(self.function_set[node.init_func].arg_operand):
            node.init_inputs[i] = random.randint(max(pos - self.INPUT_CGP_LEVELS, -self.number_of_inputs), pos - 1)
            node.weights[i] = random.uniform(self.weight_range[0], self.weight_range[1])
        node.init_output = pos

        return node

    def _determine_active_nodes(self):
        # For determination of which nodes are active
        # Also, every node is checked in the reverse order
        n_active = 0
        for node in reversed(self.nodes):
            if node.active:
                n_active += 1
                for i in range(self.function_set[node.init_func].arg_operand):
                    init_input = node.init_inputs[i]
                    if init_input >= 0:  # a node (not an input)
                        self.nodes[init_input].active = True
        if Verb:
            print("Active genes: ", n_active)

    def eval(self, *args):
        # Evaluating CGP individual output
        if not self._active_determined:
            self._determine_active_nodes()
            self._active_determined = True
        # Evaluating Forward Pass
        for node in self.nodes:
            if node.active:
                inputs = []
                for i in range(self.function_set[node.init_func].arg_operand):
                    init_input = node.init_inputs[i]
                    w = node.weights[i]
                    if init_input < 0:
                        inputs.append(args[-init_input - 1] * w)
                    else:
                        inputs.append(self.nodes[init_input].output * w)
                node.output = self.function_set[node.init_func](*inputs)
        return self.nodes[-1].output

    def mutate(self, mut_rate=0.01):
        # Modifiable individual for mutation
        child = copy.deepcopy(self)
        for pos, node in enumerate(child.nodes):
            # Mutating gene function
            if random.random() < mut_rate:
                node.init_func = random.choice(range(len(self.function_set)))
            # Mutating the input connection genes
            arg_operand = self.function_set[node.init_func].arg_operand
            for i in range(arg_operand):
                if node.init_inputs[i] is None or random.random() < mut_rate:
                    node.init_inputs[i] = random.randint(max(pos - self.INPUT_CGP_LEVELS, -self.number_of_inputs), pos - 1)
                if node.weights[i] is None or random.random() < mut_rate:
                    node.weights[i] = random.uniform(self.weight_range[0], self.weight_range[1])
            # None of the individuals are active at the beginning
            node.active = False
        for i in range(1, self.number_of_outputs + 1):
            child.nodes[-i].active = True
        child.fitness = None
        child._active_determined = False
        return child

def protected_div(a, b):
    if abs(b) < 1e-6:
        return a
    return a / b

fs = [General_Function(op.add, 2), General_Function(op.sub, 2), General_Function(op.mul, 2), General_Function(protected_div, 2), General_Function(op.neg, 1)]
Individual_Genetic_Program.function_set = fs
Individual_Genetic_Program.max_arg_operand = max(f.arg_operand for f in fs)


def evolve(pop_evo, mut_rate, mu, lambda_):
    # Integrating the lambda evolution strategy
    pop_evo = sorted(pop_evo, key=lambda ind: ind.fitness)
    parents = pop_evo[-mu:]
    # Generating new children of lambda, mutation as offspring
    offspring = []
    for _ in range(lambda_):
        parent = random.choice(parents)
        offspring.append(parent.mutate(mut_rate))
    return parents + offspring


def create_population(n):
    return [Individual_Genetic_Program() for _ in range(n)]
