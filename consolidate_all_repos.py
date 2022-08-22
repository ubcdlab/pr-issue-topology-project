import json
import sys
import networkx as nx

def read_json_from_file(TARGET_REPO_FILE_NAME):
    PATH = f'data/graph_{TARGET_REPO_FILE_NAME}.json'
    data = None
    with open(PATH, 'r') as file:
        data = json.load(file)
    return data

def construct_graph(graph_json, TARGET_REPO):
    graph = nx.Graph()
    for node in graph_json['nodes']:
        graph.add_node(node['id'], 
                repo=TARGET_REPO)
    for edge in graph_json['links']:
        graph.add_edge(edge['source'], edge['target'], type=edge['link_type'])
    return graph

def write_json_to_file(nodes):
    with open(f'unified_json/result.json', 'w') as f:
        f.write(json.dumps(nodes, sort_keys=False, separators=(',', '\n')))

def main():
    TARGET_REPO_ARRAY = sys.argv[1:]
    nodes = []
    for TARGET_REPO in TARGET_REPO_ARRAY:
        TARGET_REPO_FILE_NAME = TARGET_REPO.replace('/', '-')
        graph_json = read_json_from_file(TARGET_REPO_FILE_NAME)
        graph = construct_graph(graph_json, TARGET_REPO)
        connected_components = nx.connected_components(graph)
        for component in connected_components:
            subgraph = graph.subgraph(component)
            for node in subgraph.nodes(data=True):
                # nodes.append({
                #     'node_number': node[0],
                #     'repo_name': node[1]['repo'],
                #     'component': list(component)
                # })
                nodes.append([node[0],
                node[1]['repo'],
                list(component)
                ])
    write_json_to_file(nodes)

if __name__ == '__main__':
    main()