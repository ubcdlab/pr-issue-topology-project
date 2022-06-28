from github import Github
import datetime
import re
import sys
import json
import pickle
import networkx as nx
import copy

TARGET_REPO_FILE_NAME = 'pykerberos'

def find_node(number, nodes):
    for item in nodes:
        if item.number == number:
            return item

def find_all_mentions(text):
    ''' 
    Github is pathological; mentions to other issues/PR
    sometimes shows up as a string literal of form '#{NUMBER}'
    and sometimes shows up as a string URL of form 'https://github.com/[REPO URL]/{pull/issue}/{NUMBER}'

    Therefore, two seperate regex are required to properly detect mentions
    and even then, I am not 100% confident about this method's accuracy
    '''

    REGEX_STRING = f'(?:https:\/\/github\.com/{TARGET_REPO})\/(?:issues|pull)\/(\d+)'
    # the above regex uses non-capturing groups for the repo URLs, so only the number (the part we want)
    # is captured.

    REGEX_NUMBER_STRING = '(?<=#)\d+'
    # the above regex uses positive lookbehind to only capture numbers (the part we want)
    # from the pattern #{NUMBER}
    if text is None:
        return []
    regex_matches = []
    regex_matches += [x.group(1) for x in re.finditer(REGEX_STRING, text)]
    regex_matches += re.findall(REGEX_NUMBER_STRING, text)
    return regex_matches # return all matches in an array

# g = Github(get_token())
# repo = g.get_repo(TARGET_REPO)
graph_dict = {}

nodes = None
comment_nodes = None
with open(f'data/nodes_{TARGET_REPO_FILE_NAME}.pk', 'rb') as fi:
    nodes = pickle.load(fi)
    print(f'Loaded {len(nodes)} post nodes.')

with open(f'data/nodes_{TARGET_REPO_FILE_NAME}_comments.pk', 'rb') as ci:
    comment_nodes = pickle.load(ci)
    print(f'Loaded {len(nodes)} comment nodes.')

working_nodes = copy.copy(nodes)
sys.exit(0)

HIGHEST_ISSUE_NUMBER = nodes[0].number
print(f'Processing {HIGHEST_ISSUE_NUMBER} nodes.')

for issue in working_nodes:
    total_links = []
    node_dict = {}

    if (issue.user.type != 'Bot'):
        total_links += find_all_mentions(issue.body)

    total_links = list(filter(lambda x: (0 < int(x) <= HIGHEST_ISSUE_NUMBER), total_links))
    node_dict['id'] = issue.number
    node_dict['type'] = 'pull_request' if issue.pull_request is not None else 'issue'
    node_dict['status'] = issue.state
    node_dict['links'] = total_links
    node_dict['finish'] = False

    if issue.pull_request is not None:
        # this ugly check is needed to find out whether a PR is merged
        # since PyGithub doesn't support this directly
        if issue.pull_request.raw_data['merged_at'] is not None:
            node_dict['status'] = 'merged'

    graph_dict['nodes'].append(node_dict)
    for link in total_links:
        graph_dict['links'].append({'source': issue.number, 'target': int(link)})

    print(f'Finished processing node {issue.number} BODY TEXT ONLY. Rate limit: {g.rate_limiting[0]}')


# Construct the graph
graph = nx.Graph()
for node in graph_dict['nodes']:
    graph.add_node(node['id'])
    print(f'Adding node {node["id"]} to graph...')
for link in graph_dict['links']:
    graph.add_edge(link['source'], link['target'])
    print(f'Adding edge {link["source"]},{link["target"]} to graph...')

# Compute the connected component
connected_components = list(nx.connected_components(graph))
for component in connected_components:
    for node in component:
        for entry in graph_dict['nodes']:
            if (entry['id'] == node):
                entry['connected_component'] = list(component)
                print(f'Adding connected component property to node {node}')

# Compute the degrees
for node in graph.degree:
    node_id = node[0]
    node_degree = node[1]
    for entry in graph_dict['nodes']:
        if (entry['id'] == node_id):
            entry['node_degree'] = node_degree
graph_dict['connected_components'] = list(map(lambda x: list(x), connected_components))

with open(f'data/graph_{TARGET_REPO_FILE_NAME}.json', 'w') as f:
    f.write(json.dumps(graph_dict, sort_keys=False, indent=4))

# for issue in nodes[1:3]:
#     total_links = []
#     node_dict = {}

#     if (issue.user.type != 'Bot'):
#         total_links += find_all_mentions(issue.body)
#     for comment in issue.get_comments():
#         if (comment.user.type != 'Bot'):
#             total_links += find_all_mentions(comment.body)

#     total_links = list(filter(lambda x: (int(x) <= HIGHEST_ISSUE_NUMBER), total_links))

#     print(f'Finished processing node {issue.number}. Rate limit: {g.rate_limiting[0]}')


# print(nodes)