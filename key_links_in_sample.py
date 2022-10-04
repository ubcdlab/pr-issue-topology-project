import csv
import json
from more_itertools import unique_everseen
from urllib.request import urlopen
import re

def main():
    PATH = f'unified_json/java_sample.csv'
    # csv_row = [['repo_name',
    #            'component_id',
    #            'link_url',
    #            'node_1_type',
    #            'node_1_id', 
    #            'node_1_author', 
    #            'node_1_num_comment', 
    #            'node_2_type', 
    #            'node_2_id', 
    #            'node_2_author',
    #            'node_2_num_comments'
    #            'link_type']]
    csv_row = [['repo_name',
                'node_type',
                'node_id',
                'node_url',
                'node_creator',
                'node_comments_count',
                'list_of_node_commentors']]
    with open(PATH) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        next(csv_reader) # skip csv header
        for row in csv_reader:
            repo_name = row[1]
            file_name = repo_name.replace('/', '-')
            with open(f'data/graph_{file_name}.json') as file:
                data = json.load(file)
            nodes_in_component = row[9].split('|')
            for node in nodes_in_component:
                link = find_link(data, node)
                source_node = find_node(data, link['source'])
                target_node = find_node(data, link['target'])
                source_node_users = set()
                source_node_users_email = set()
                target_node_users = set()
                target_node_users_email = set()
                for event in source_node['event_list']:
                    if event['event'] not in ['commented', 'cross-referenced', 'referenced']:
                        continue
                    if event['author'] != 'None':
                        source_node_users.add(event['author'])
                        try:
                            user_url = event['author']
                            html_page = urlopen(user_url).read()
                            # ([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+


                for event in target_node['event_list']:
                    if event['author'] != 'None':
                        target_node_users.add(event['author'])
                source_node_url = f"http://github.com/{repo_name}/issues/{source_node['id']}"
                csv_row_entry = [repo_name,
                                 source_node['type'],
                                 source_node['id'],
                                 source_node_url,
                                 source_node['node_creator'],
                                 source_node['comments'],
                                 list(source_node_users)
                                 ]
                csv_row.append(csv_row_entry)
                target_node_url = f"http://github.com/{repo_name}/issues/{target_node['id']}"
                csv_row_entry = [repo_name,
                                 target_node['type'],
                                 target_node['id'],
                                 target_node_url,
                                 target_node['node_creator'],
                                 target_node['comments'],
                                 list(target_node_users)
                                 ]
                csv_row.append(csv_row_entry)
    with open(f'unified_json/csv_contributors.csv', 'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerows(csv_row)
    with open(f'unified_json/csv_contributors.csv', 'r') as file, open('unified_json/csv_contributors_nod.csv', 'w') as out_file:
        out_file.writelines(unique_everseen(file))
    return

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