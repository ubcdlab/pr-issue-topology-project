import json
import sys
import networkx as nx


def read_json_from_file(TARGET_REPO_FILE_NAME):
    PATH = f'data/graph_{TARGET_REPO_FILE_NAME}.json'
    data = None
    with open(PATH, 'r') as file:
        data = json.load(file)
    return data

def construct_graph(graph_json):
    graph = nx.DiGraph()
    for node in graph_json['nodes']:
        graph.add_node(node['id'], 
                type=node['type'], 
                status=node['status'], 
                created_at=node['creation_date'], 
                closed_at=node['closed_at'],
                event_list=node['event_list'])
    for edge in graph_json['links']:
        graph.add_edge(edge['source'], edge['target'], type=edge['link_type'])
    return graph

def sample_graph_component_density_bucket(graph):
    density_buckets = []
    return density_buckets

def sample_graph_component_order_bucket(graph):
    undirected_graph = graph.to_undirected()
    connected_components = list(nx.connected_components(undirected_graph))

    TOTAL_SAMPLE_SIZE = 100
    order_buckets = []
    # Sample from the extremes
    isolated_components = []
    oversized_components = [] # defined as component size >= 16
    for component in connected_components:
        if len(connected_components)


def main():
    TARGET_REPO_ARRAY = sys.argv[1:]
    csv_rows = []
    for TARGET_REPO in TARGET_REPO_ARRAY:
        TARGET_REPO_FILE_NAME = TARGET_REPO.replace('/', '-')
        graph_json = read_json_from_file(TARGET_REPO_FILE_NAME)
        graph = construct_graph(graph_json)

if __name__ == '__main__':
    main()