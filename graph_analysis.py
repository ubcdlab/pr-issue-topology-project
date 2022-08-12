import json
import sys 
import networkx as nx
import csv

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

def max_number_possible_edges_directed(graph):
    n = graph.number_of_nodes()
    return (n * (n - 1))

def max_number_possible_edges_directed_nodenum(n):
    return (n * (n - 1))

def calculate_fixes_relationship_component_percentage(graph, TARGET_REPO_FILE_NAME, csv_rows):
    undirected_graph = graph.to_undirected()
    csv_column_header = ['key_field', 'repo_name', 'component_number', 'component_size', 'percentage', 'fixes_count', 'edge_count', 'component_nodes']
    connected_components = list(nx.connected_components(undirected_graph))
    counter = 0
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
        csv_row_entry = [f'{TARGET_REPO_FILE_NAME}+{counter}',
                        TARGET_REPO_FILE_NAME,
                        index,
                        len(component), 
                        (fixes_count / component_edge_count),
                        fixes_count,  
                        component_edge_count,
                        component]
        csv_rows.append(csv_row_entry)
        counter += 1
    return csv_column_header, csv_rows

def calculate_connected_component_density(graph):
    csv_column_header = ['component', 'component_size', 'percentage', 'edge_count', 'max_possible', 'component_nodes']
    csv_rows = []
    undirected_graph = graph.to_undirected()
    connected_components = list(nx.connected_components(undirected_graph))
    for index, component in enumerate(connected_components):
        component_subgraph = graph.subgraph(component)
        if component_subgraph.number_of_nodes() <= 1:
            continue
        
        component_edge_count = component_subgraph.number_of_edges()
        max_number_possible_edges = max_number_possible_edges_directed(component_subgraph)

        csv_row_entry = [index,
                        component_subgraph.number_of_nodes(), 
                        (component_edge_count / max(max_number_possible_edges, 1)) * 100, # prevent division by 0 
                        component_edge_count,  
                        max_number_possible_edges,
                        component]
        # print(csv_row_entry)
        csv_rows.append(csv_row_entry)
    return csv_column_header, csv_rows

def calculate_summary(graph, TARGET_REPO_FILE_NAME, csv_rows):
    csv_column_header = ['key_field', 'repo_name', 'component_number', 'component_size', 'edge_count', 'max_possible', 'subgraph_density']
    undirected_graph = graph.to_undirected()
    connected_components = list(nx.connected_components(undirected_graph))
    counter = 0
    for index, component in enumerate(connected_components):
        component_subgraph = graph.subgraph(component)
        component_edge_count = component_subgraph.number_of_edges()
        csv_row_entry = [f'{TARGET_REPO_FILE_NAME}+{counter}',
                        TARGET_REPO_FILE_NAME,
                        index,
                        len(component),
                        component_edge_count,
                        max_number_possible_edges_directed_nodenum(len(component)),
                        component_edge_count / max(max_number_possible_edges_directed_nodenum(len(component)), 1)]
        csv_rows.append(csv_row_entry)
        counter += 1
    return csv_column_header, csv_rows

def calculate_work_done_before_merge(graph, TARGET_REPO_FILE_NAME, csv_rows):
    csv_column_header = ['key_field', 'repo_name', 'component_number', 'component_size', 'component_nodes', 'preexisting_nodes', 'preexisting_node_count', 'percentage', 'last_merged_node', 'merged_node_count']
    undirected_graph = graph.to_undirected()
    connected_components = list(nx.connected_components(undirected_graph))
    counter = 0
    for index, component in enumerate(connected_components):
        if len(component) <= 1:
            continue
        component_subgraph = undirected_graph.subgraph(component)
        merged_nodes = list(filter(lambda d: d[1]['status'] == 'merged', component_subgraph.nodes(data=True)))
        if len(merged_nodes) < 1:
            continue
        most_recent_merged_node = merged_nodes[-1] # last element is most recent
        for node_number, node_attribute in merged_nodes:
            if node_attribute['closed_at'] < most_recent_merged_node[1]['closed_at']:
                most_recent_merged_node = (node_number, node_attribute)
        # Having found the most recent merged node, find out how much of the connected
        # component existed before the node was merged
        post_merge_nodes = []
        for node in component_subgraph.nodes(data=True):
            if node == most_recent_merged_node:
                continue
            if node[1]['created_at'] > most_recent_merged_node[1]['closed_at']:
                post_merge_nodes.append(node)

        csv_row_entry = [f'{TARGET_REPO_FILE_NAME}+{counter}',
                        TARGET_REPO_FILE_NAME,
                        index,
                        len(component),
                        component,
                        list(map(lambda x: x[0], post_merge_nodes)),
                        len(post_merge_nodes),
                        len(post_merge_nodes) / len(component),
                        most_recent_merged_node[0],
                        len(merged_nodes)]
        csv_rows.append(csv_row_entry)
        counter += 1
    return csv_column_header, csv_rows

def calculate_mean_comments_per_component_before_after_merge(graph, TARGET_REPO_FILE_NAME, csv_rows):
    csv_column_header = ['repo_name', 'component_number', 'component_size', 'component_nodes', 'comments_count', 'comments_count_after_merge', 'last_merged_node']
    undirected_graph = graph.to_undirected()
    connected_components = list(nx.connected_components(undirected_graph))
    for index, component in enumerate(connected_components):
        component_subgraph = undirected_graph.subgraph(component)
        comments = []
        comments_after_merge = []
        merged_nodes = list(filter(lambda d: d[1]['status'] == 'merged', component_subgraph.nodes(data=True)))
        if len(merged_nodes) < 1:
            continue
        most_recent_merged_node = merged_nodes[-1]
        for node_number, node_attribute in merged_nodes:
            if node_attribute['closed_at'] > most_recent_merged_node[1]['closed_at']:
                most_recent_merged_node = (node_number, node_attribute)
        for node in component_subgraph.nodes(data=True):
            comments_list = list(filter(lambda x: x['event'] == 'commented', node[1]['event_list']))
            if node[1]['created_at'] > most_recent_merged_node[1]['closed_at']:
                comments_after_merge.append(comments_list)
            else:
                comments.append(node)
        csv_row_entry = [TARGET_REPO_FILE_NAME,
                        index,
                        len(component),
                        component,
                        len(comments),
                        len(comments_after_merge),
                        most_recent_merged_node[0]]
        csv_rows.append(csv_row_entry)
    return csv_column_header, csv_rows

def calculate_mean_comments_per_node(graph, TARGET_REPO_FILE_NAME, csv_rows):
    return

def calculate_diameter_density_per_component(graph, TARGET_REPO_FILE_NAME, csv_rows):
    csv_column_header = ['key_field', 'repo_name', 'component_number', 'component_size', 'component_nodes', 'component_diameter', 'subgraph_density']
    undirected_graph = graph.to_undirected()
    connected_components = list(nx.connected_components(undirected_graph))
    counter = 0
    for index, component in enumerate(connected_components):
        component_subgraph = undirected_graph.subgraph(component)
        diameter = nx.diameter(component_subgraph)

        edges_in_subgraph = graph.subgraph(component).number_of_edges()
        max_possible_edges_directed = max_number_possible_edges_directed_nodenum(len(component))

        csv_row_entry = [f'{TARGET_REPO_FILE_NAME}+{counter}',
                        TARGET_REPO_FILE_NAME,
                        index,
                        len(component),
                        component,
                        diameter,
                        edges_in_subgraph / max(max_possible_edges_directed, 1)]
        csv_rows.append(csv_row_entry)
        print(f'Loaded component {component} in {TARGET_REPO_FILE_NAME}')
        counter += 1
    return csv_column_header, csv_rows
    
def calculate_mean_authors_per_component_before_after_merge(graph, TARGET_REPO_FILE_NAME, csv_rows):
    csv_column_header = ['repo_name', 'component_number', 'component_size', 'component_nodes', 'authors_count', 'authors_count_after_merge', 'last_merged_node']
    undirected_graph = graph.to_undirected()
    connected_components = list(nx.connected_components(undirected_graph))
    for index, component in enumerate(connected_components):
        component_subgraph = undirected_graph.subgraph(component)
        authors = set()
        authors_after_merge = set()
        merged_nodes = list(filter(lambda d: d[1]['status'] == 'merged', component_subgraph.nodes(data=True)))
        if len(merged_nodes) < 1:
            continue
        most_recent_merged_node = merged_nodes[-1]
        for node_number, node_attribute in merged_nodes:
            if node_attribute['closed_at'] > most_recent_merged_node[1]['closed_at']:
                most_recent_merged_node = (node_number, node_attribute)
        for node in component_subgraph.nodes(data=True):
            # filter out events that are both less significant and do not have authoring information 
            authors_list = list(filter(lambda x: x['event'] not in ['committed', 'closed', 'renamed'], node[1]['event_list']))
            authors_list = set(map(lambda x: x['author'], authors_list))
            if node[1]['created_at'] > most_recent_merged_node[1]['closed_at']:
                authors_after_merge.update(authors_list)
            else:
                authors.update(authors_list)
        csv_row_entry = [TARGET_REPO_FILE_NAME,
                        index,
                        len(component),
                        component,
                        len(authors),
                        len(authors_after_merge),
                        most_recent_merged_node[0]]
        csv_rows.append(csv_row_entry)
    return csv_column_header, csv_rows

def calculate_graph_connected_component_sizes_distribution(graph, TARGET_REPO_FILE_NAME, csv_rows):
    csv_column_header = ['key_field', 'repo_name', 'component_number', 'component_size', 'component_nodes']
    undirected_graph = graph.to_undirected()
    connected_components = list(nx.connected_components(undirected_graph))
    counter = 0
    for index, component in enumerate(connected_components):
        csv_row_entry = [f'{TARGET_REPO_FILE_NAME}+{counter}',
                        TARGET_REPO_FILE_NAME,
                        index,
                        len(component),
                        component]
        csv_rows.append(csv_row_entry)
        counter += 1
    return csv_column_header, csv_rows

def master_function(graph, TARGET_REPO_FILE_NAME, csv_rows):
    csv_column_header = ['key_field', 
                         'repo_name', 
                         'component_number', 
                         'component_nodes',
                         'component_size',
                         'authors',
                         'comments',
                         ]
    return


def main():
    TARGET_REPO_ARRAY = sys.argv[1:]
    csv_rows = []
    for TARGET_REPO in TARGET_REPO_ARRAY:
        TARGET_REPO_FILE_NAME = TARGET_REPO.replace('/', '-')
        graph_json = read_json_from_file(TARGET_REPO_FILE_NAME)
        graph = construct_graph(graph_json)

        # csv_column_header, csv_rows = calculate_summary(graph, TARGET_REPO_FILE_NAME, csv_rows)
        # csv_merge_column_header, csv_merge_rows = calculate_work_done_before_merge(graph, TARGET_REPO_FILE_NAME, csv_rows)
        # csv_author_column_header, csv_author_rows = calculate_mean_authors_per_component(graph, TARGET_REPO_FILE_NAME, csv_rows)
        # csv_comment_column_header, csv_comment_rows = calculate_mean_comments_per_component(graph, TARGET_REPO_FILE_NAME, csv_rows)
        csv_diameter_column_header, csv_diameter_rows = calculate_diameter_density_per_component(graph, TARGET_REPO_FILE_NAME, csv_rows)
        # csv_component_size_column_header, csv_rows = calculate_graph_connected_component_sizes_distribution(graph, TARGET_REPO_FILE_NAME, csv_rows)
        # csv_fixes_column_header, csv_fixes_rows = calculate_fixes_relationship_component_percentage(graph, TARGET_REPO_FILE_NAME, csv_rows)


    # write_csv_to_file(csv_column_header, csv_rows, 'density2', '')
    # write_csv_to_file(csv_merge_column_header, csv_merge_rows, 'work_done_after_merge', '')
    # write_csv_to_file(csv_column_header, csv_rows, 'component_size_distribution', '')
    write_csv_to_file(csv_diameter_column_header, csv_diameter_rows, 'component_diameter', '')
    # write_csv_to_file(csv_component_size_column_header, csv_rows, 'component_size_dist', '')
    # write_csv_to_file(csv_fixes_column_header, csv_fixes_rows, 'fixes', '')


if __name__ == '__main__':
    main()
