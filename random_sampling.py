import datetime
import json
import networkx as nx
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

if __name__ == '__main__':
    main()