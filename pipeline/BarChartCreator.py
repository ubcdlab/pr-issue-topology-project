import datetime
import re
from github import Github
import picklereader
import networkx as nx
import json
import os

class BarChartCreator(picklereader.PickleReader):
    def __init__(self, github_token, target_repo_list):
        self.target_repo_list = target_repo_list
    
    def create_vis_for_all_repo(self):
        for target_repo in self.target_repo_list:
            graph_dict = self.create_vis_json_for_repo(target_repo)
            self.write_json_to_file(graph_dict, target_repo)
    
    def write_json_to_file(self, graph_dict, target_repo):
        target_repo_no_slash = target_repo.replace('/', '-')
        PATH = os.path.abspath('..')
        with open(f'{PATH}/data/graph_{target_repo_no_slash}.json', 'w') as f:
            f.write(json.dumps(graph_dict, sort_keys=False, indent=4))
        print(f'Saved result to data/graph_{target_repo_no_slash}.json')

    def create_vis_json_for_repo(self, target_repo):
        graph = nx.Graph()
        analysis_dict = {}

        nodes, node_list, comment_list, timeline_list, review_comment_list = self.read_repo_local_file(None, target_repo)
        for index, issue in enumerate(nodes):
            graph.add_node(issue.number)
            links_dict = []
            issue_timeline = timeline_list[-index-1]
            issue_timeline = list(filter(lambda x: x.event == 'cross-referenced' and x.source.issue.repository.full_name == target_repo, issue_timeline))
            for mention in issue_timeline:
                # Tracks INCOMING MENTIONS
                links_dict.append({
                    'number': mention.source.issue.number,
                })
            for link in links_dict:
                # add link to the graph
                graph.add_edge(link['number'], issue.number)
        connected_components = list(nx.connected_components(graph))
        max_component_size = 0
        for component in connected_components:
            max_component_size = max(len(component), max_component_size)
        for counter in range(1, max_component_size + 1):
            analysis_dict.append({
                counter: []
            })
        for isolated_node in list(nx.isolates(graph)):
            analysis_dict['1'].append([isolated_node])
        
        


        
        



