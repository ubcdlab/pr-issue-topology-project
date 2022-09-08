import csv
import json
import pickle

def main():
    PATH = f'unified_json/java_sample.csv'
    csv_row = [['repo_name',
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
                csv_row_entry = [repo_name,
                                 link['comment_link'],
                                 source_node['type'],
                                 source_node['id'],
                                 source_node['node_creator'],
                                 source_node['comments'],
                                 target_node['type'],
                                 target_node['id'],
                                 target_node['node_creator'],
                                 target_node['comments'],
                                 link['link_type']]
                csv_row.append(csv_row_entry)
    with open(f'unified_json/csv_sampled_links.csv', 'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerows(csv_row)

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