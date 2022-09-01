import csv
import json
import sys
import networkx as nx
import re

def read_json_from_file(TARGET_REPO_FILE_NAME):
    PATH = f'data/graph_{TARGET_REPO_FILE_NAME}.json'
    data = None
    with open(PATH, 'r') as file:
        data = json.load(file)
    return data

def construct_graph(graph_json, TARGET_REPO):
    # To add more data into the output file
    # you probably want to change this function, which
    # adds data to nodes (so you can include more info in
    # connected components later)
    graph = nx.Graph()
    for node in graph_json['nodes']:
        authors = set()
        for event in node['event_list']:
            event_author = event['author']
            if event_author == 'None' or not event_author.startswith('https://github.com'):
                continue
            authors.add(event_author)
        graph.add_node(node['id'], authors=list(authors))
    for edge in graph_json['links']:
        graph.add_edge(edge['source'], edge['target'], type=edge['link_type'])
    return graph

def write_json_to_file(nodes):
    with open(f'unified_json/result.json', 'w') as f:
        f.write(json.dumps(nodes, sort_keys=False, indent=4))

def max_number_possible_edges_directed_nodenum(n):
    return (n * (n - 1))

def write_csv_to_file(csv_column_header, csv_rows):
    PATH = f'unified_json/result_simple.csv'
    with open(PATH, 'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerow(csv_column_header)
        csvwriter.writerows(csv_rows)

def main():
    TARGET_REPO_ARRAY = sys.argv[1:]
    components = []
    csv_rows = []
    csv_column_header = ['key', 'repo_name', 'size', 'diameter', 'density', 'authors']
    magic_counter = 0
    for TARGET_REPO in TARGET_REPO_ARRAY:
        TARGET_REPO_FILE_NAME = TARGET_REPO.replace('/', '-')
        graph_json = read_json_from_file(TARGET_REPO_FILE_NAME)
        graph = construct_graph(graph_json, TARGET_REPO)
        connected_components = nx.connected_components(graph)
        for component in connected_components:
            if len(component) <= 1:
                continue
            subgraph = graph.subgraph(component)
            edges_in_subgraph = graph.subgraph(component).number_of_edges()
            max_possible_edges_directed = max_number_possible_edges_directed_nodenum(len(component))
            list_of_nodes = list(subgraph.nodes(data=True))
            set_of_authors = set()
            for node in list_of_nodes:
                set_of_authors.update(node[1]['authors'])
            csv_rows.append([magic_counter, 
            TARGET_REPO,
            len(component),
            nx.diameter(subgraph),
            edges_in_subgraph / max(max_possible_edges_directed, 1),
            list(set_of_authors)
            ])
            magic_counter += 1
    # write_json_to_file(components)
    write_csv_to_file(csv_column_header, csv_rows)

if __name__ == '__main__':
    main()