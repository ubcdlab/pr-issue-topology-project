import json
import csv
import random
from datetime import date
from dateutil.relativedelta import relativedelta
from more_itertools import unique_everseen
import operator

def read_json_from_file():
    PATH = f'unified_json/result.json'
    data = None
    with open(PATH, 'r') as file:
        data = json.load(file)
    return data

def write_json_to_file(nodes):
    return
    # with open(f'unified_json/random_sample_result.json', 'w') as f:
    #     f.write(json.dumps(nodes, sort_keys=False, indent=4))

def generate_data_vis_file(sampled_component):
    graph_dict = {
        'nodes': [],
        'links': []
    }
    for component in sampled_component:
        for node in component:
            data = None
            repo_name = node['repo_name']
            repo_file_name = repo_name.replace('/', '-')
            with open(f'data/graph_{repo_file_name}.json') as file:
                data = json.load(file)
            component_id = node['component_id']
            links = find_link(data, node['node_id'])
            for link in links:
                source_node = find_node(data, link['source'])
                target_node = find_node(data, link['target'])
                source_node_id = str(component_id) + str(source_node['id'])
                target_node_id = str(component_id) + str(target_node['id'])
                source_node_dict = {
                    'id': source_node_id,
                    'type': source_node['type'],
                    'status': source_node['status'],
                    'url': 'https://github.com/' + repo_name + '/issues/' + str(source_node['id']),
                    'component_id': component_id,
                    'display_id': source_node['id']
                }
                target_node_dict = {
                    'id': target_node_id,
                    'type': target_node['type'],
                    'status': target_node['status'],
                    'url': 'https://github.com/' + repo_name + '/issues/' + str(target_node['id']),
                    'component_id': component_id,
                    'display_id': target_node['id']
                }
                link_dict = {
                    'source': source_node_id,
                    'target': target_node_id,
                    'comment_link': link['comment_link'],
                    'component_id': component_id
                }
                graph_dict['nodes'].append(source_node_dict)
                graph_dict['nodes'].append(target_node_dict)
                graph_dict['links'].append(link_dict)
    graph_dict['nodes'] = list(unique_everseen(graph_dict['nodes']))
    graph_dict['links'] = list(unique_everseen(graph_dict['links']))
    with open(f'unified_json/random_sample_vis.json', 'w') as f:
        f.write(json.dumps(graph_dict, sort_keys=False, indent=4))
    return

def main():
    unix_six_months_ago = 1649228400
    condensed_file = read_json_from_file()
    sample = []
    component_id = []
    for component in condensed_file:
        keep = True
        for node in component:
            if node['created_at'] < unix_six_months_ago:
                keep = False
        if keep:
            sample.append(component)
    # while len(sample) < 100:
    #     hand = random.choice(condensed_file)
    #     condensed_file.remove(hand)
    #     keep = True
    #     for node in hand:
    #         if node['created_at'] < unix_six_months_ago:
    #             keep = False
    #     if keep:
    #         sample.append(hand)
    print(f'Sampled {len(sample)} items.')
    # write_json_to_file(sample)
    # generate_data_vis_file(sample)
    csv_rows = [['repo_name',
                'component_id',
                'url',
                'node_id',
                'comment_count'],
                'component_size']
    for component in sample:
        component_id.append({
            'component_id': component[0]['component_id'],
            'size': len(component)
        })
        for node in component:
            row = [node['repo_name'],
                    node['component_id'],
                    node['url'],
                    node['node_id'],
                    node['comment_count'],
                    len(component)]
            csv_rows.append(row)
    with open(f'unified_json/csv_all_young_sample_nodes.csv', 'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerows(csv_rows)
    # with open(f'unified_json/copy_paste_this.txt', 'w') as f:
    #     component_id.sort(key=operator.itemgetter('size'), reverse=True)
    #     for id in component_id:
    #         f.write(f'<option value="{id["component_id"]}">{id["component_id"]} (Size: {id["size"]})</option>\n')
    #     f.close()

def find_link(js, target_node):
    links = []
    for link in js['links']:
        if link['source'] == int(target_node) or link['target'] == int(target_node):
            links.append(link)
    return links

def find_node(js, target_node):
    for node in js['nodes']:
        if node['id'] == int(target_node):
            return node

if __name__ == '__main__':
    main()