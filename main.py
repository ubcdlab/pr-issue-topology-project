from github import Github
import traceback
import datetime
import re
import sys
import json
import networkx as nx
import pickle
from os.path import exists

TARGET_REPO = '02strich/pykerberos'
TARGET_REPO_FILE_NAME = 'pykerberos'

def get_token():
    # get personal access token
    # from a file named token.txt
    token = None
    try:
        with open('.token', 'r') as f:
            token = f.read()
            print('Github token read OK')
    except IOError:
        pass
    return token

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

def fetch_data():
    g = Github(get_token())
    graph_dict = {}
    repo = g.get_repo(TARGET_REPO)
    repo_url = repo.html_url

    print(f'Downloading repo: {repo_url} with {repo.open_issues} open issues')
    nodes = list(repo.get_issues(state='all', sort='created', direction='desc'))
    issue_and_pr_numbers = nodes.copy()
    issue_and_pr_numbers = list(map(lambda x: x.number, issue_and_pr_numbers))
    # sys.exit(1)
    print(f'Loaded {len(nodes)} nodes from repo.')
    
    with open(f'data/nodes_{TARGET_REPO_FILE_NAME}.pk', 'wb') as fi:
        pickle.dump(nodes, fi)


    node_progress_file_exist = exists(f'data/nodes_{TARGET_REPO_FILE_NAME}_comments.pk')
    node_list = None
    comment_list = []

    if node_progress_file_exist is True:
        # we aren't startin from scratch
        with open(f'data/nodes_{TARGET_REPO_FILE_NAME}_progress.pk', 'rb') as fi:
            node_list = pickle.load(fi)
        with open(f'data/nodes_{TARGET_REPO_FILE_NAME}_comments.pk', 'rb') as fi:
            comment_list = pickle.load(fi)
    else:
        # we never crawled this repo before
        with open(f'data/nodes_{TARGET_REPO_FILE_NAME}.pk', 'rb') as npf:
            node_list = pickle.load(npf)

    print(f'Nodes remaining to load: {len(node_list)}')

    HIGHEST_ISSUE_NUMBER = nodes[0].number

    graph_dict['repo_url'] = repo_url
    graph_dict['issue_count'] = 0
    graph_dict['pull_request_count'] = 0
    graph_dict['nodes'] = []
    graph_dict['links'] = []

    pit_limiter = 0

    try:
        while len(node_list) > 0:
            if pit_limiter >= 5:
                raise Exception('PIT LIMITER')
            # pit_limiter += 1
            issue = node_list.pop(0)
            total_links = []
            node_dict = {}

            if (issue.user.type != 'Bot'):
                total_links += find_all_mentions(issue.body)
            node_comments = issue.get_comments()
            for comment in node_comments:
                if (comment.user.type != 'Bot'):
                    total_links += find_all_mentions(comment.body)

            total_links = list(filter(lambda x: (0 < int(x) <= HIGHEST_ISSUE_NUMBER) and int(x) in issue_and_pr_numbers, total_links))
            # print(total_links)

            node_dict['id'] = issue.number
            node_dict['type'] = 'pull_request' if issue.pull_request is not None else 'issue'
            node_dict['status'] = issue.state
            node_dict['links'] = total_links

            if issue.pull_request is not None:
                # this ugly check is needed to find out whether a PR is merged
                # since PyGithub doesn't support this directly
                if issue.pull_request.raw_data['merged_at'] is not None:
                    node_dict['status'] = 'merged'

            graph_dict['nodes'].append(node_dict)
            for link in total_links:
                graph_dict['links'].append({'source': issue.number, 'target': int(link)})

            print(f'Finished processing node {issue.number}. Rate limit: {g.rate_limiting[0]}')
            # node_list.remove(issue)
            comment_list.append(list(node_comments))
    except Exception as e:
        print(e)
    finally:
        with open(f'data/nodes_{TARGET_REPO_FILE_NAME}_progress.pk', 'wb') as fi:
            pickle.dump(node_list, fi)
        with open(f'data/nodes_{TARGET_REPO_FILE_NAME}_comments.pk', 'wb') as fi:
            pickle.dump(comment_list, fi)
    g.get_rate_limit()
    print(f'Finished downloading entire repo. Rate limit: {g.rate_limiting[0]}')

    return graph_dict

def compute_network_statistics(data):
    # Construct the graph
    graph = nx.Graph()
    for node in data['nodes']:
        graph.add_node(node['id'])
    for link in data['links']:
        graph.add_edge(link['source'], link['target'])

    # Compute the connected component
    connected_components = list(nx.connected_components(graph))
    for component in connected_components:
        for node in component:
            for entry in data['nodes']:
                if (entry['id'] == node):
                    entry['connected_component'] = list(component)

    # Compute the degrees
    for node in graph.degree:
        node_id = node[0]
        node_degree = node[1]
        for entry in data['nodes']:
            if (entry['id'] == node_id):
                entry['node_degree'] = node_degree
    data['connected_components'] = list(map(lambda x: list(x), connected_components))
    return data

redownload = 'reload' in sys.argv
write_to_file = 'write' in sys.argv
result = None

if redownload == True:
    result = fetch_data()
else:
    f = open(f'data/graph_{TARGET_REPO_FILE_NAME}.json')
    result = json.load(f)

result = compute_network_statistics(result)

with open(f'data/graph_{TARGET_REPO_FILE_NAME}.json', 'w') as f:
    # save result to disk
    if write_to_file == True:
        f.write(json.dumps(result, sort_keys=False, indent=4))
        print(f'Saved result to data/graph_{TARGET_REPO_FILE_NAME}.json')
    else:
        print('Did not save result to file; to save result, run script with "write" in arguments')



