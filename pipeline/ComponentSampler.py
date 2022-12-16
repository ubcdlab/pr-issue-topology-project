import json
import picklereader
import networkx as nx
import random
from pathlib import Path  

SAMPLE_SIZE = 100

class ComponentSampler(picklereader.PickleReader):
    def __init__(self, github_token, target_repo_list):
        self.target_repo_list = target_repo_list
        self.all_repo_component = []
        self.component_id_keyfield_counter = 0
    
    def load_all_repo_component(self):
        for target_repo in self.target_repo_list:
            self.load_repo_component(target_repo)
        graph_dict = self.sample_component()
        self.write_json_to_file(graph_dict)

    def write_json_to_file(self, graph_dict):
        PATH = Path(__file__).resolve().parents[1]
        for entry in graph_dict:
            del entry['component_nodes']
        with open(f'{PATH}/unified_json/recent_sampling.json', 'w') as f:
            f.write(json.dumps(graph_dict, sort_keys=False, indent=4, default=lambda o: ''))
    
    def find_issue(self, nodes, id):
        for issue in nodes:
            if issue.number == id:
                return issue
    
    def load_repo_component(self, target_repo):
        graph = nx.Graph()
        links_dict = []

        nodes, node_list, comment_list, timeline_list, review_comment_list = self.read_repo_local_file(None, target_repo)
        for index, issue in enumerate(nodes):
            graph.add_node(issue.number)
            issue_timeline = timeline_list[-index-1]
            issue_timeline = list(filter(lambda x: x.event == 'cross-referenced' and x.source.issue.repository.full_name == target_repo, issue_timeline))
            for mention in issue_timeline:
                # Tracks INCOMING MENTIONS
                links_dict.append({
                    'source': mention.source.issue.number,
                    'target': issue.number
                })
                graph.add_edge(mention.source.issue.number, issue.number)
        connected_components = list(nx.connected_components(graph))
        for component in connected_components:
            component_authors = set()
            total_comment_count = 0
            subgraph = graph.subgraph(component)
            edge_count = graph.subgraph(component).number_of_edges() # edgy
            issue_list = []
            for node in component:
                issue = self.find_issue(nodes, node)
                component_authors.add(issue.user.html_url)
                total_comment_count += issue.comments
                issue_list.append(issue)

            self.all_repo_component.append({
                'repo_name': target_repo,
                'component_id': self.component_id_keyfield_counter,
                'component_nodes': list(issue_list),
                'component_nodes_id': list(component),
                # 'component_authors': list(component_authors),
                # 'comment_count': total_comment_count,
                'diameter': nx.diameter(subgraph),
                'density': edge_count / max((edge_count * (edge_count - 1)), 1),
                'url': f'https://github.com/{target_repo}/issues/{list(component)[0]}'
            })
            self.component_id_keyfield_counter += 1
        
    def sample_component(self):
        filtered = list(filter(self.filter_criteria, self.all_repo_component))
        return random.sample(filtered, min(SAMPLE_SIZE, len(filtered)))

    def filter_criteria(self, component):
        UNIX_SIX_MONTHS_AGO = 1649228400
        for node in component['component_nodes']:
            if node.created_at.timestamp() < UNIX_SIX_MONTHS_AGO:
                return False
        return True
