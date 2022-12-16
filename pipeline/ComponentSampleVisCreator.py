import json
from pathlib import Path

class ComponentSampleVisCreator(object):
    def __init__(self, github_token, target_repo_list):
        pass

    def read_sample_file(self):
        PATH = Path(__file__).resolve().parents[1]
        with open(f'{PATH}/unified_json/recent_sampling.json', 'r') as f:
            return json.load(f)
    
    def write_json_to_file(self, graph_dict):
        PATH = Path(__file__).resolve().parents[1]
        with open(f'{PATH}/unified_json/sample_visualise.json', 'w') as f:
            f.write(json.dumps(graph_dict, sort_keys=False, indent=4))
        print(f'Saved result to unified_json/sample_visualise.json')

    def create_vis_for_sample(self):
        sample_json = self.read_sample_file()
        graph_dict = {
            'nodes': [],
            'links': []
        }
        for component in sample_json:
            for node in component['component_nodes_data']:
                node_dict = {
                    'id': str(component['component_id']) + str(node['id']),
                    'type': node['type'],
                    'status': node['status'],
                    'url': f'https://github.com/{component["repo_name"]}/issues/{node["id"]}',
                    'component_id': str(component['component_id']),
                    'display_id': node['id']
                }
                graph_dict['nodes'].append(node_dict)
            for link in component['links']:
                link_dict = {
                    'source': f'{component["component_id"]}{link[0]}',
                    'target': f'{component["component_id"]}{link[1]}',
                    'comment_link': f'https://github.com/{component["repo_name"]}/issues/{link[0]}',
                    'component_id': component['component_id']
                }
                graph_dict['links'].append(link_dict)
        self.write_json_to_file(graph_dict)

