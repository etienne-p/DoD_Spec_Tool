import sys
import yaml

class System:
    def __init__(self, name):
        self.name = name
        self.dependencies = [] # a list holding label of systems we depend on
        self.inputs = [] # a list of component types the system takes in input
        self.outputs = [] # a list of components the system mutates/generates

class Context:
    def __init__(self, name, components):
        self.name = name
        self.components = components # a list of supported components, mostly to catch up typos in the yaml file

def graph_to_dot(graph):
    """
    generates a .dot (graphviz) representation of the graph
    """
    pass

def compute_edges(systems):
    """
    compute edges based on system dependencies
    """
    return [(dep, s.name) for s in systems for dep in s.dependencies]

def compile_dot(context, inputs, systems):
    """
    builds a graph based on system dependencies
    """
    edges = compute_edges(systems)

    edges_decl = ["%s -- %s" % e for e in edges]

    input_decl_prefix = "node [shape=ellipse, style=\"\"];"
    input_names = [" %s;" % i for i in inputs]
    input_decl = input_decl_prefix + input_names

    sys_decl_prefix = "node [shape=box, style=\"filled\", fillcolor=\"#dddddd\"];"
    sys_names = [" %s;" % s.name for s in systems]
    sys_decl = sys_decl_prefix + sys_names

    #TODO comp node: comp that are not produced by a depended on system are fetched form world

    node_decl = "\n".join([input_decl, sys_decl, comp_decl])

    dot = "\n".join([
        "graph ER {",
        "rankdir = \"LR\"",
        "\n".join(node_decl),
        "\n".join(edges_decl),
        "label = \"\n\n%s\";" % context.name
        "fontsize=20;",
        "}"])
    return dot


def parse_system(context, data):
    s = System(data["name"])
    for i in data["in"]:
        assert(i in context.components), "Unexpected component %s" % i
        s.inputs.append(i)
    for i in data["out"]:
        assert(i in context.components), "Unexpected component %s" % i
        s.outputs.append(i)
    # TODO if systems are not ordered we have to defer error checking
    for i in data["depend_on"]:
        s.dependencies.append(i)
    return s

def parse_yaml_data(data):
    context = Context(data["Label"] if "Label" in data else "DataFlow", data["Components"])
    inputs = data["Inputs"]
    systems = [parse_system(context, s) for s in data["Systems"]]
    return context, inputs, systems

def parse_yaml(path):
    """
    parses the yaml file and returns a collection of inputs and systems
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
    context, inputs, systems = parse_yaml(path)
    dot = compile_dot(context, inputs, systems)
    print(dot)
    # TODO render with graphviz

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("expected 2 or more command line arguments, aborted.")
        exit()
    path = sys.argv[1]
    # TODO regex based check?
    yaml_to_graph(path)

