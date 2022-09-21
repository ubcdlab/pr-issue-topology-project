import csv
import json
import pickle
from more_itertools import unique_everseen

def main():
    PATH = f'unified_json/java_sample.csv'
    csv_row = [['repo_name',
               'component_id',
               'link_url',
               'node_1_type',
               'node_1_id', 
               'node_1_author', 
               'node_1_num_comment', 
               'node_2_type', 
               'node_2_id', 
               'node_2_author',
               'node_2_num_comments'
               'link_type']]
    with open(PATH) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        next(csv_reader) # skip csv header
        graph_dict = {
            'nodes': [],
            'links': []
        }
        for row in csv_reader:
            component_id = row[0]
            repo_name = row[1]
            file_name = repo_name.replace('/', '-')
            with open(f'data/graph_{file_name}.json') as file:
                data = json.load(file)
            nodes_in_component = row[9].split('|')
            for node in nodes_in_component:
                link = find_link(data, node)
                source_node = find_node(data, link['source'])
                target_node = find_node(data, link['target'])
                source_node_id = str(component_id) + str(source_node['id'])
                target_node_id = str(component_id) + str(target_node['id'])
                source_node_dict = {
                    'id': source_node_id,
                    'type': source_node['type'],
                    'status': source_node['status'],
                }
                target_node_dict = {
                    'id': target_node_id,
                    'type': target_node['type'],
                    'status': target_node['status'],
                }
                link_dict = {
                    'source': source_node_id,
                    'target': target_node_id,
                    'comment_link': link['comment_link']
                }
                graph_dict['nodes'].append(source_node_dict)
                graph_dict['nodes'].append(target_node_dict)
                graph_dict['links'].append(link_dict)
    with open(f'unified_json/sample_visualise.json', 'w') as f:
        f.write(json.dumps(graph_dict, sort_keys=False, indent=4))

def find_link(js, target_node):
    for link in js['links']:
        if link['source'] == int(target_node) or link['target'] == int(target_node):
            return link

def find_node(js, target_node):
    for node in js['nodes']:
        if node['id'] == int(target_node):
            return node


if __name__ == '__main__':
    main()