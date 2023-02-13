from gspan_mining import gSpan
import networkx as nx
from sys import argv

target_data_path = None
for arg in argv:
    if "target" in arg:
        target_data_path = arg.split("=")[-1]

if not target_data_path:
    print("Must provide target data path (run convert_network_to_gspan_format.py first!)")
    exit(1)

min_support = 1000
for arg in argv:
    if "support" in arg:
        min_support = int(arg.split("=")[-1])

size = 5
for arg in argv:
    if "size" in arg:
        size = int(arg.split("=")[-1])

gspan = gSpan(
    target_data_path,
    min_support=min_support,
    max_num_vertices=size,
    min_num_vertices=size,
    is_undirected=False,
    where=True,
    visualize=True,
)
gspan.run()
del gspan.graphs[0]

if not len(gspan.graphs.values()):
    print("No frequent subgraphs with given parameters found.")
    exit(0)

for graph in gspan.graphs.values():
    gnx = nx.Graph()
    vlbs = {vid: v.vlb for vid, v in graph.vertices.items()}
    elbs = {}
    for vid, v in graph.vertices.items():
        gnx.add_node(vid, label=v.vlb)
    for vid, v in graph.vertices.items():
        for to, e in v.edges.items():
            if vid < to:
                gnx.add_edge(vid, to, label=e.elb)
                elbs[(vid, to)] = e.elb
    print(gnx)
