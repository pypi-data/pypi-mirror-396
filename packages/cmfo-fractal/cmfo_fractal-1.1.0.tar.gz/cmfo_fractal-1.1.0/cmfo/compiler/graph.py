"""
CMFO Compiler - Fractal Graph
=============================

Represents a computation as a directed acyclic graph (DAG) of 
Geometric Triangles and Rhombuses.

CMFO does not "compute" linearly; it structures dependencies.
"""

class FractalNode:
    """
    A node in the fractal computation graph.
    Can represent an Input, a Gate (Triangle), or a Memory (Rhombus).
    """
    def __init__(self, name, operation, parents=None):
        self.name = name
        self.operation = operation
        self.parents = parents or []
        self._cached_result = None

    def evaluate(self, context):
        """
        Recursively evaluate the node.
        """
        # 1. Fetch input values (from parents or context)
        input_values = []
        for p in self.parents:
            input_values.append(p.evaluate(context))
            
        # 2. Apply operation
        # If it's a Source (no parents), look up in context
        if not self.parents:
            return context.get(self.name, self.operation)
            
        # 3. Compute
        # We assume operation is a callable that takes *inputs
        return self.operation(*input_values)

class FractalGraph:
    """
    Container for the fractal dependency structure.
    """
    def __init__(self, name="main"):
        self.name = name
        self.nodes = {}
        self.outputs = []
        
    def add_input(self, name):
        node = FractalNode(name, operation=None, parents=[])
        self.nodes[name] = node
        return node
        
    def add_op(self, name, operation, parents):
        node = FractalNode(name, operation, parents)
        self.nodes[name] = node
        return node
        
    def set_output(self, node):
        self.outputs.append(node)
