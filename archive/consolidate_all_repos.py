import csv
from gc import collect
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
        event_timestamp = []
        for event in node['event_list']:
            event_author = event['author']
            if event_author == 'None' or not event_author.startswith('https://github.com'):
                continue
            authors.add(event_author)
        for event_time in node['event_list']:
            event_timestamp.append(event_time['created_at'])
        graph.add_node(node['id'], 
                       authors=list(authors), 
                       comments=node['comments'], 
                       repo_contributors=node['repo_contributors'],
                       component_id=node['component_id'],
                       created_at=node['creation_date'],
                       updated_at=node['updated_at'],
                       event_timestamps=event_timestamp)
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
    collected_components = []
    for TARGET_REPO in TARGET_REPO_ARRAY:
        TARGET_REPO_FILE_NAME = TARGET_REPO.replace('/', '-')
        graph_json = read_json_from_file(TARGET_REPO_FILE_NAME)
        graph = construct_graph(graph_json, TARGET_REPO)
        connected_components = nx.connected_components(graph)
        for component in connected_components:
            if len(component) <= 1:
                continue
            subgraph = graph.subgraph(component)
            # edges_in_subgraph = graph.subgraph(component).number_of_edges()
            # max_possible_edges_directed = max_number_possible_edges_directed_nodenum(len(component))
            list_of_nodes = list(subgraph.nodes(data=True))
            list_of_nodes_no_data = list(subgraph.nodes())
            set_of_authors = set()
            nodes_in_component = []
            total_comments = 0
            for node in list_of_nodes:
                node_data = node[1]
                set_of_authors.update(node[1]['authors'])
                total_comments += node[1]['comments']
                nodes_in_component.append({
                    'component_id': node_data['component_id'],
                    'repo_name': TARGET_REPO,
                    'node_id': node[0],
                    # 'diameter': nx.diameter(subgraph),
                    # 'density': edges_in_subgraph / max(max_possible_edges_directed, 1),
                    'component_authors': ','.join(set_of_authors),
                    'url': f'https://github.com/{TARGET_REPO}/issues/{node[0]}',
                    'comment_count': total_comments,
                    'repo_contributors': node_data['repo_contributors'],
                    'component_nodes': ','.join([str(x) for x in list_of_nodes_no_data]),
                    'created_at': node_data['created_at'],
                    'updated_at': node_data['updated_at'],
                    'event_timestamps': node_data['event_timestamps']
                })
            collected_components.append(nodes_in_component)
            # csv_rows.append([list_of_nodes[0][1]['component_id'], 
            #     TARGET_REPO,
            #     len(component),
            #     nx.diameter(subgraph),
            #     edges_in_subgraph / max(max_possible_edges_directed, 1),
            #     '|'.join(set_of_authors),
            #     'https://github.com/' + TARGET_REPO + '/issues/' + str(list_of_nodes[0][0]),
            #     total_comments,
            #     node[1]['repo_contributors'],
            #     '|'.join([str(x) for x in list_of_nodes_no_data])])
    write_json_to_file(collected_components)
    # write_csv_to_file(csv_column_header, csv_rows)

if __name__ == '__main__':
    main()