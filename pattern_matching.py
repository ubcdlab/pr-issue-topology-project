import json
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
                event_list=node['event_list'],
                comment_count=node['comments'],
                node_author=node['node_creator'])
    for edge in graph_json['links']:
        graph.add_edge(edge['source'], edge['target'], type=edge['link_type'])
    return graph



def main():
    graph_json = read_json_from_file('tiny-dnn-tiny-dnn')
    graph = construct_graph(graph_json)
    # list(nx.connected_components(graph))
    undirected_graph = graph.to_undirected()
    connected_components = list(nx.connected_components(undirected_graph))

    graph_pattern = nx.DiGraph()
    graph_pattern.add_node(332)
    graph_pattern.add_node(415)
    graph_pattern.add_node(68)
    graph_pattern.add_edge(415, 332)
    graph_pattern.add_edge(68, 332)

    for index, component in enumerate(connected_components):
        component_subgraph = graph.subgraph(component)
        GM = nx.isomorphism.GraphMatcher(component_subgraph, graph_pattern)
        if GM.subgraph_is_isomorphic():
            print(component)
            print('Yes')


if __name__ == '__main__':
    main()