from github import Github
import traceback
import datetime
import re
import sys
import json
import networkx as nx

TARGET_REPO = 'jekyll/jekyll-admin'
TARGET_REPO_FILE_NAME = 'jekyll-admin'

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

def get_highest_issue_number(repo):
    latest_issue = list(repo.get_issues(state='all', since=datetime.datetime(2022, 5, 1), direction='desc'))
    return latest_issue[0].number

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

    print(f'Downloading repo: {repo.html_url} with {repo.open_issues} open issues')
    nodes = list(repo.get_issues(state='all', sort='created', direction='asc'))
    print(f'Loaded {len(nodes)} nodes from repo.')

    HIGHEST_ISSUE_NUMBER = nodes[0].number

    graph_dict['repo_url'] = repo.html_url
    graph_dict['issue_count'] = 0
    graph_dict['pull_request_count'] = 0
    graph_dict['nodes'] = []
    graph_dict['links'] = []

    for issue in nodes:
        total_links = []
        node_dict = {}

        if (issue.user.type != 'Bot'):
            total_links += find_all_mentions(issue.body)
        for comment in issue.get_comments():
            if (comment.user.type != 'Bot'):
                total_links += find_all_mentions(comment)

        total_links = list(filter(lambda x: (int(x) <= HIGHEST_ISSUE_NUMBER), total_links))

        node_dict['id'] = issue.number
        node_dict['type'] = 'pull_request' if issue.pull_request is not None else 'issue'
        node_dict['status'] = item.state
        node_dict['links'] = total_links

        if issue.pull_request is not None:
            # this ugly check is needed to find out whether a PR is merged
            # since PyGithub doesn't support this directly
            if issue.pull_request.raw_data['merged_at'] is not None:
                node_dict['status'] = 'merged'

        graph_dict['nodes'].append(node_dict)
        for links in total_links:
            graph_dict['links'].append({'source': issue.number, 'target': int(link)})

        print(f'Finished loading node number: {issue_number}; Rate Limit Remaining: {g.rate_limiting[0]}')


    # for issue_number in range(1, HIGHEST_ISSUE_NUMBER + 1):
    #     # go through every possible issue/PR number
    #     try:
    #         item = repo.get_issue(issue_number) # get the issue
    #         total_links = [] # initialise array of matches, set to empty
    #         node_dict = {}

    #         if (item.user.type != 'Bot'): # filter out links/mentions made by bot accounts 
    #             total_links += find_all_mentions(item.body) # find all mentions in issue/PR description

    #         for comment in item.get_comments(): # go through every single comment
    #             if (comment.user.type != 'Bot'): # filter out links/mentions made by bot accounts
    #                 total_links += find_all_mentions(comment.body) # find all mentions in a specific comment
            
    #         # filter out mentions to other projects, right now we catch mentions
    #         # to other projects by removing links with an issue/PR number that is higher
    #         # than the project of concern
    #         total_links = list(filter(lambda x: (int(x) <= HIGHEST_ISSUE_NUMBER), total_links))

    #         ''' Github API treats both issue and PR as issues (PRs are issues with code),
    #             API docs direct us to distinguish between the two by checking the pull_request key
    #             which is None for issues
    #         '''
    #         node_dict['id'] = issue_number
    #         node_dict['type'] = 'pull_request' if item.pull_request is not None else 'issue'
    #         node_dict['status'] = item.state # whether an issue/PR is open or closed
    #         node_dict['links'] = total_links

    #         if item.pull_request is not None:
    #             # this ugly check is needed to find out whether a PR is merged
    #             # since GitHub doesn't support this directly
    #             pull_request_is_merged = repo.get_issue(issue_number).as_pull_request().merged
    #             if pull_request_is_merged is True:
    #                 node_dict['status'] = 'merged'

    #         # update the dictionary storing the graph toplogy 
    #         graph_dict['nodes'].append(node_dict)
    #         print(f'Finished loading node number: {issue_number}; Rate Limit Remaining: {g.rate_limiting[0]}')

    #         for link in total_links:
    #             graph_dict['links'].append({'source': issue_number, 'target': int(link)})

    #     except Exception as e:
    #         # Exceptions usually happens, when we try to load a number 
    #         # that doesn't correspond to an issue or pull request
    #         # idk why Github let this happens
    #         # s = traceback.format_exc()
    #         # serr = "there were errors:\n%s\n" % (s)
    #         # sys.stderr.write(serr)
    #         node_dict['id'] = issue_number
    #         node_dict['type'] = 'error'
    #         node_dict['status'] = 'error'
    #         node_dict['links'] = []
    #         graph_dict['nodes'].append(node_dict)
    #         print(e)

    print('Finished downloading entire repo.')
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
    f = open('data/graph.json')
    result = json.load(f)

result = compute_network_statistics(result)
# print(result)

with open(f'data/graph_{TARGET_REPO_FILE_NAME}.json', 'w') as f:
    # save result to disk
    if write_to_file == True:
        f.write(json.dumps(result, sort_keys=False, indent=4))
        print(f'Saved result to data/graph_{TARGET_REPO_FILE_NAME}.json')
    else:
        print('Did not save result to file; to save result, run script with "write" in arguments')



