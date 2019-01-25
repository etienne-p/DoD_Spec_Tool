import sys
import yaml
import itertools
import subprocess
from graphviz import Digraph

class System:
    def __init__(self, name):
        self.name = name
        self.dependencies = [] # a list holding label of systems we depend on
        self.inputs = [] # a list of component types the system takes in input
        self.outputs = [] # a list of components the system mutates/generates

class Context:
    def __init__(self, name, inputs, components, ):
        self.name = name
        self.inputs = inputs
        self.components = components # a list of supported components, mostly to catch up typos in the yaml file
    def valid_source(self, src):
        return src in self.inputs or src in self.components

def compute_ancestor_data_dependency(system):
    """
    provides a list of components recursively provided by dependencies
    """
    def compute_data_dependency_rec(data, system):
        for d in system.dependencies:
            for c in d.outputs:
                if c not in data:
                    data[c] = d.name
            compute_data_dependency_rec(data, d)

    data = dict()
    # skip direct ancestors, already connected
    for s in system.dependencies:
        compute_data_dependency_rec(data, s)
    return data

def compute_edges(context, systems, graph):
    """
    compute edges based on system dependencies
    components are either provided by dependencies or, by default, World
    returns a list of edges and a list of "filter" nodes
    """
    edges = []
    used_components = []
    # each system introduces its input edges
    for s in systems:
        # always one edge representing node input
        name_in = "%s_in" % s.name # implicit node
        name_out = "%s_out" % s.name
        graph.edge(name_in, s.name)
        # one edge per dependency
        for d in s.dependencies:
            graph.edge("%s_out" % d.name, name_in)
        # ancestor dependencies
        ancestor_dependencies = compute_ancestor_data_dependency(s)
        # based on those dependencies, add edges to ancestor systems
        world_connected = False
        for i in s.inputs:
            if i in ancestor_dependencies:
                graph.edge("%s_out" % ancestor_dependencies[i], name_in)
            elif i in context.inputs:
                graph.edge(i, name_in)
            elif not world_connected:
                # anything that does not come from input or dependencies
                # is assumed to come from World
                world_connected = True
                graph.edge("World", name_in)
        for o in s.outputs:
            graph.edge(s.name, name_out)

    return edges

def make_graph(context, systems):
    """
    builds a graph based on system dependencies
    """
    font = 'courier'
    graph = Digraph(context.name, filename='%s.gv' % context.name)
    graph.attr(rankdir='LR', fontsize='20', label="\n\n"+context.name)

    compute_edges(context, systems, graph)

    for i in context.inputs:
        graph.node(i, shape='cds', style='filled', fillcolor='#d8d8d8', fontname=font)
    for s in systems:
        graph.node(s.name, shape='box3d', style='filled', fillcolor='#bad4ff', fontname=font)

    def record_decl(comps):
        return "| ".join(["<f%s>%s" % (i, c) for i, c in enumerate(comps)])

    # component sets depend on systems IO
    for r in [("%s_in" % s.name, s.inputs) for s in systems] + [("%s_out" % s.name, s.outputs) for s in systems]:
        graph.node(r[0], record_decl(r[1]), shape='record', fontsize='10', fontname=font)

    return graph

def parse_system(context, data):
    s = System(data["name"])
    for i in data["in"]:
        assert(context.valid_source(i)), "Unexpected source %s" % i
        s.inputs.append(i)
    for i in data["out"]:
        assert(context.valid_source(i)), "Unexpected source %s" % i
        s.outputs.append(i)
    return s

def parse_yaml_data(data):
    inputs = data["Inputs"] if "Inputs" in data else []
    if not "World" in inputs:
        inputs.append("World")
    label = data["Label"] if "Label" in data else "DataFlow"
    context = Context(label, inputs, data["Components"])
    systems_dep = [(parse_system(context, s), s["depend_on"] if "depend_on" in s else []) for s in data["Systems"]]
    # having instanciated systems, assign dependencies
    systems_dict = dict((s[0].name, s[0]) for s in systems_dep)
    systems = []
    # detect typo in system names
    for r in systems_dep:
        s = r[0]
        for d in r[1]:
            s.dependencies.append(systems_dict[d])
        systems.append(s)
    return context, systems

def parse_yaml(path):
    """
    parses the yaml file and returns a context and a collection of inputs and systems
    """
    with open(path, 'r') as stream:
        try:
            data = yaml.load(stream)
            return parse_yaml_data(data)
        except yaml.YAMLError as exc:
            print(exc)
    return -1, -1, -1

# turns DoD concepts described in yaml file to a visual representation
def yaml_to_graph(path):
    context, systems = parse_yaml(path)
    graph = make_graph(context, systems)
    print(graph.source)
    dot_filename = "%s.dot" % context.name
    with open(dot_filename, 'w') as dot_file:
        dot_file.write(graph.source)
    subprocess.run(["dot", "-Tpng", dot_filename, "-o", "%s.png" % context.name])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("expected 2 or more command line arguments, aborted.")
        exit()
    path = sys.argv[1]
    yaml_to_graph(path)

