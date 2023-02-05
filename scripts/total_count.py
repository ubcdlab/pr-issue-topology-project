from .helpers import all_graphs, to_json

pathlist = all_graphs()
count = 0
for path in pathlist:
    path_str = str(path)
    graph_json = to_json(path_str)
    count += len(graph_json["nodes"])

print(f"Total number of nodes: {count}")
