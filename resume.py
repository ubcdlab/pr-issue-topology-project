from github import Github
import datetime
import re
import sys
import json
import pickle

TARGET_REPO = 'facebook/react'
TARGET_REPO_FILE_NAME = 'react'

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

g = Github(get_token())
repo = g.get_repo(TARGET_REPO)
graph_dict = {}

nodes = None
with open('nodes.pk', 'rb') as fi:
    nodes = pickle.load(fi)
    print(f'Loaded {len(nodes)} Nodes.')

graph_dict['issue_count'] = 0
graph_dict['pull_request_count'] = 0
graph_dict['nodes'] = []
graph_dict['links'] = []


for issue in nodes[1:3]:
    total_links = []
    node_dict = {}

    if (issue.user.type != 'Bot'):
        total_links += find_all_mentions(issue.body)
    for comment in issue.get_comments():
        if (comment.user.type != 'Bot'):
            total_links += find_all_mentions(comment.body)

    total_links = list(filter(lambda x: (int(x) <= HIGHEST_ISSUE_NUMBER), total_links))

    print(f'Finished processing node {issue.number}. Rate limit: {g.rate_limiting[0]}')

# print(nodes)