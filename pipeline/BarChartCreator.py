import picklereader
import networkx as nx
import json
from pathlib import Path

class BarChartCreator(picklereader.PickleReader):
    def __init__(self, github_token, target_repo_list):
        self.target_repo_list = target_repo_list
    
    def create_vis_for_all_repo(self):
        for target_repo in self.target_repo_list:
            graph_dict = self.create_vis_json_for_repo(target_repo)
            self.write_json_to_file(graph_dict, target_repo)
    
    def write_json_to_file(self, graph_dict, target_repo):
        target_repo_no_slash = target_repo.replace('/', '-')
        PATH = Path(__file__).resolve().parents[1]
        with open(f'{PATH}/data/structure_{target_repo_no_slash}.json', 'w') as f:
            f.write(json.dumps(graph_dict, sort_keys=False, indent=4))
        print(f'Saved result to data/structure_{target_repo_no_slash}.json')
    
    def find_node(self, nodes, id):
        for node in nodes:
            if node.number == id:
                return node
    
    def find_link(self, links_dict, node_1, node_2):
        for link in links_dict:
            if link['source'] == node_1.number and link['target'] == node_2.number:
                return node_1, node_2
            elif link['target'] == node_1.number and link['source'] == node_2.number:
                return node_2, node_1

    def compute_node_order(self, source_node, sink_node):
        source_node_type = 'pull_request' if source_node.pull_request is not None else 'issue'
        sink_node = 'pull_request' if sink_node.pull_request is not None else 'issue'
        return [source_node_type, sink_node]

    def create_vis_json_for_repo(self, target_repo):
        graph = nx.Graph()
        pattern_json = {}
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
        connected_component_sizes = set()

        pattern_json = {
            '1': {
                'isolated': []
            },
            '2': {
                'duo_issue_issue': [],
                'duo_issue_pr': [],
                'duo_pr_pr': [],
                'duo_pr_issue': []
            }
        }
        for component in connected_components:
            connected_component_sizes.add(len(component))
        connected_component_sizes.remove(1)
        connected_component_sizes.discard(2)
        for size in connected_component_sizes:
            pattern_json[str(size)] = {
                'general': []
            }
        # Populate the isoated nodes list in pattern_json
        for isolated_node in list(nx.isolates(graph)):
            pattern_json['1']['isolated'].append([isolated_node])
        counter = 0
        # now populate the duo nodes list in pattern_json
        for component in connected_components:
            if len(component) != 2:
                continue
            counter += 1
            component = list(component)
            component.sort()

            lower_number_node = self.find_node(nodes, component[0])
            higher_number_node = self.find_node(nodes, component[1])

            source_node, sink_node = self.find_link(links_dict, lower_number_node, higher_number_node)
            ordering = self.compute_node_order(source_node, sink_node)
            if ordering == ['issue', 'issue']:
                pattern_json['2']['duo_issue_issue'].append([source_node.number, sink_node.number])
            if ordering == ['issue', 'pull_request']:
                pattern_json['2']['duo_issue_pull_request'].append([source_node.number, sink_node.number])
            if ordering == ['pull_request', 'pull_request']:
                pattern_json['2']['duo_pr_pr'].append([source_node.number, sink_node.number])
            if ordering == ['pull_request', 'issue']:
                pattern_json['2']['duo_pr_issue'].append([source_node.number, sink_node.number])

        # now populate the rest
        for component in connected_components:
            component_size = len(component)
            if component_size < 3:
                continue
            pattern_json[str(component_size)]['general'].append(list(component))
        return pattern_json
        
        


        
        



