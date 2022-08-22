import json
import sys
import networkx as nx


def read_json_from_file():
    PATH = f'unified_json/result.json'
    with open(PATH, 'r') as file:
        data = json.load(file)
    return data

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
    # populate isolated components first
    for node in graph:
        # if 
        return
    return


def main():
    raw_data = read_json_from_file()
    sample_graph_component_order_bucket(raw_data)

if __name__ == '__main__':
    main()