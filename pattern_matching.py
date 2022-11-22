

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
    TARGET_REPO_ARRAY = sys.argv[1:]
    csv_rows = []

if __name__ == '__main__':
    main()