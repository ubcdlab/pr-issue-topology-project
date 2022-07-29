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

def write_csv_to_file(csv_column_header, csv_rows, REPO_NAME, filename=''):
    if filename != '':
        filename = '_' + filename
    PATH = f'csv/csv_{REPO_NAME}{filename}.csv'
    with open(PATH, 'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow(csv_column_header)
        csvwriter.writerows(csv_rows)

def construct_graph(graph_json):
    graph = nx.Graph()
    for node in graph_json['nodes']:
        graph.add_node(node['id'])
    for edge in graph_json['links']:
        graph.add_edge(edge['source'], edge['target'], type=edge['link_type'])
    return graph

def max_number_possible_edges_undirected(graph):
    n = graph.number_of_nodes()
    return (n * (n - 1))

def calculate_fixes_relationship_component_percentage(graph):
    csv_column_header = ['component', 'percentage', 'fixes_count', 'edge_count', 'component_nodes']
    csv_rows = []
    connected_components = list(nx.connected_components(graph))
    for index, component in enumerate(connected_components):
        component_subgraph = graph.subgraph(component)
        component_edge_count = component_subgraph.number_of_edges()
        fixes_count = 0

        if component_edge_count == 0:
            continue
        for edge in component_subgraph.edges.data():
            edge_type = edge[2]['type']
            if edge_type == 'fixes':
                fixes_count += 1
        csv_row_entry = [index, 
                        (fixes_count / component_edge_count) * 100, # prevent division by 0 
                        fixes_count,  
                        component_edge_count,
                        component]
        csv_rows.append(csv_row_entry)
    return csv_column_header, csv_rows

def calculate_connected_component_density(graph):
    csv_column_header = ['component', 'percentage', 'edge_count', 'max_possible', 'component_nodes']
    csv_rows = []
    connected_components = list(nx.connected_components(graph))
    for index, component in enumerate(connected_components):
        component_subgraph = graph.subgraph(component)
        if component_subgraph.number_of_nodes() <= 1:
            continue
        
        component_edge_count = component_subgraph.number_of_edges()
        max_number_possible_edges = max_number_possible_edges_undirected(component_subgraph)

        csv_row_entry = [index, 
                        (component_edge_count / max(max_number_possible_edges, 1)) * 100, # prevent division by 0 
                        component_edge_count,  
                        max_number_possible_edges,
                        component]
        # print(csv_row_entry)
        csv_rows.append(csv_row_entry)
    return csv_column_header, csv_rows

def main():
    TARGET_REPO = sys.argv[1]
    TARGET_REPO_FILE_NAME = TARGET_REPO.replace('/', '-')
    graph_json = read_json_from_file(TARGET_REPO_FILE_NAME)
    graph = construct_graph(graph_json)

    csv_column_header, csv_rows = calculate_connected_component_density(graph)
    write_csv_to_file(csv_column_header, csv_rows, TARGET_REPO_FILE_NAME, '')

    csv_column_header, csv_rows = calculate_fixes_relationship_component_percentage(graph)
    write_csv_to_file(csv_column_header, csv_rows, TARGET_REPO_FILE_NAME, 'fixes')


if __name__ == '__main__':
    main()
