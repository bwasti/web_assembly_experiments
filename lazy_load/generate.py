import random
import networkx as nx

generated_dir = 'generated/'

def gen_dag(nodes, edges, depth):
  G = nx.DiGraph()
  for i in range(nodes):
    G.add_node(i)
  while edges > 0:
    a = random.randint(0, nodes-1)
    b = a
    while b == a:
      b = random.randint(0, nodes-1)
    G.add_edge(a, b)
    if nx.is_directed_acyclic_graph(G) and (len(nx.dag_longest_path(G)) <= depth):
      edges -= 1
    else:
      G.remove_edge(a, b)
  return G

dag = gen_dag(1000, 3000, 5)
def rand_op():
  infix_op = ["*", "+", "^", "*", "+", "%"];#, "-", "%", "&", "|", "^"]
  return random.choice(infix_op)

def gen_func(dag, n):
  out = "";
  for use in dag.successors(n):
    out += f"unsigned f_{use}(unsigned);\n"
  out += "\n";
  out += f"unsigned f_{n}(unsigned x) {{\n"
  for use in dag.successors(n):
    out += f"  x = x {rand_op()} f_{use}(x);\n"
  for i in range(2000):#random.randint(1000, 2000)):
    k = random.randint(1,2**30-1)
    out += f"  x = x {rand_op()} {k}u;\n"
  k = random.randint(1,2**30-1)
  out += f"  unsigned y = x {rand_op()} {k}u;\n"
  out += f"  return y == 0 ? {k}u : y;\n";
  out += "}\n"
  return out

for n in dag.nodes:
  contents = gen_func(dag, n)
  with open(generated_dir + f'f_{n}.cpp', 'w') as f:
    f.write(contents)
