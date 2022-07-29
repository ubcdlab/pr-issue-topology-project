import json
import sys 
import pickle
import networkx as nx
import csv
from os.path import exists

def read_json_from_file(TARGET_REPO_FILE_NAME):
    PATH = f'data/graph_{TARGET_REPO_FILE_NAME}.json'
    data = None
    with open(PATH, 'r') as file:
        data = json.load(file)
    return data

def write_csv_to_file(csv_column, csv_rows, filename):
    return

def construct_graph(graph_json):
    graph = nx.Graph()
    for node in graph_json['nodes']:
        graph.add_node(node['id'])
    for edge in graph_json['links']:
        graph.add_edge(edge['source'], edge['target'], type=edge['link_type'])
    return graph

def calculate_fixes_relationship_component_percentage(graph):
    return

def max_number_possible_edges_undirected(graph):
    n = graph.number_of_nodes()
    return (n * (n - 1))

def calculate_connected_component_stats(graph):
    csv_column = ['component', 'percentage', 'edge_count', 'max_possible', 'component_nodes']
    csv_row = []
    connected_components = list(nx.connected_components(graph))
    for index, component in enumerate(connected_components):
        component_subgraph = graph.subgraph(component)
        if component_subgraph.number_of_nodes() <= 1:
            continue
        
        component_number_of_edges = component_subgraph.number_of_edges()
        max_number_possible_edges = max_number_possible_edges_undirected(component_subgraph)

        csv_row_entry = [index, 
                        (component_number_of_edges / max(max_number_possible_edges, 1)) * 100, # prevent division by 0 
                        component_number_of_edges,  
                        max_number_possible_edges,
                        component]
        # print(csv_row_entry)
        csv_row.append(csv_row_entry)

def main():
    TARGET_REPO = sys.argv[1]
    TARGET_REPO_FILE_NAME = TARGET_REPO.replace('/', '-')
    graph_json = read_json_from_file(TARGET_REPO_FILE_NAME)
    graph = construct_graph(graph_json)
    calculate_connected_component_stats(graph)

if __name__ == '__main__':
    main()
