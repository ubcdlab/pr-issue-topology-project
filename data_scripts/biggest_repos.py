from sys import path

path.append("..")

from data_scripts.helpers import all_graphs, fetch_repo, to_json

repo_to_size_map = {}
for graph in all_graphs():
    path = str(graph)
    repo_to_size_map[fetch_repo(path_str=path, from_graph=True)] = len(
        to_json(path)["nodes"]
    )

repo_to_size_map = dict(
    sorted(repo_to_size_map.items(), key=lambda x: x[1], reverse=True)
)
print(repo_to_size_map)
