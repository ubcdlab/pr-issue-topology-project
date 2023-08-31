import json
import math
import picklereader
import networkx as nx
import random
from pathlib import Path  

SAMPLE_SIZE = 100
DEFAULT_SIMILARITY_THRESHOLD = 0.2

class DiversitySamplerStage1(picklereader.PickleReader):
    def __init__(self, github_token, target_repo_list):
        self.target_repo_list = target_repo_list
        self.all_repo_component = []
        self.component_id_keyfield_counter = 1
    
    def load_all_repo_component(self):
        for target_repo in self.target_repo_list:
            self.load_repo_component(target_repo)
        
        csv_output = self.process_component()
        self.write_csv_to_file(csv_output)

    def write_csv_to_file(self, csv_output):
        PATH = Path(__file__).resolve().parents[1]
        with open(f'{PATH}/unified_json/recent_sampling.json', 'w') as f:
            pass            
    
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
            component_node_dict = []
            for node in component:
                issue = self.find_issue(nodes, node)
                component_authors.add(issue.user.html_url)
                total_comment_count += issue.comments
                issue_list.append(issue)
                component_node_dict.append({
                    'id': issue.number,
                    'type': 'pull_request' if issue.pull_request is not None else 'issue',
                    'status': issue.state
                })
            self.all_repo_component.append({
                'repo_name': target_repo,
                'component_id': self.component_id_keyfield_counter,
                'component_nodes': list(issue_list),
                'component_nodes_data': component_node_dict,
                # 'component_authors': list(component_authors),
                # 'comment_count': total_comment_count,
                'links': [list(e) for e in subgraph.edges],
                'diameter': nx.diameter(subgraph),
                'density': edge_count / max((edge_count * (edge_count - 1)), 1),
                'url': f'https://github.com/{target_repo}/issues/{list(component)[0]}'
            })
            self.component_id_keyfield_counter += 1
    
    def process_component(self):
        collected_components = []
        csv_rows = []
        set_of_authors = set()
        total_comments = 0
        for component in self.all_repo_component:
            for node in component['component_nodes']:
                set_of_authors.update([node.user.html_url])
                total_comments += node.comments
            # key,repo_name,size,diameter,density,component_authors,url,comment_count,repo_contributors,component_nodes
            csv_rows.append([
                component['component_id'],
                component['repo_name'],
                len(component),
                component['diameter'],
                component['density'],
                '|'.join(set_of_authors),
                f'https://github.com/{component["repo_name"]}/issues/{component["component_nodes_data"][0]["id"]}',
                total_comments,
            ])
        return self.all_repo_component
