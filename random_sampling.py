import json
import csv
import random
from datetime import date
from dateutil.relativedelta import relativedelta

def read_json_from_file():
    PATH = f'unified_json/result.json'
    data = None
    with open(PATH, 'r') as file:
        data = json.load(file)
    return data

def write_json_to_file(nodes):
    with open(f'unified_json/random_sample_result.json', 'w') as f:
        f.write(json.dumps(nodes, sort_keys=False, indent=4))

def main():
    unix_six_months_ago = 1649228400
    condensed_file = read_json_from_file()
    sample = []
    while len(sample) < 100:
        hand = random.choice(condensed_file)
        condensed_file.remove(hand)
        keep = True
        for node in hand:
            if node['created_at'] < unix_six_months_ago:
                keep = False
        if keep:
            sample.append(hand)
    print(f'Sampled {len(sample)} items.')
    write_json_to_file(sample)
    csv_rows = [['repo_name',
                'component_id',
                'url',
                'node_id',
                'comment_count']]
    for component in sample:
        for node in component:
            row = [node['repo_name'],
                            node['component_id'],
                            node['url'],
                            node['node_id'],
                            node['comment_count']]
            csv_rows.append(row)
    with open(f'unified_json/csv_random_sample.csv', 'w') as csv_file:
        csvwriter = csv.writer(csv_file)
        csvwriter.writerows(csv_rows)

if __name__ == '__main__':
    main()