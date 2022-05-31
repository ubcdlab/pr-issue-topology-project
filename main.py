from github import Github
import datetime
import re
import sys
import json

TARGET_REPO = 'jekyll/jekyll-admin'

def get_token():
    # get personal access token
    # from a file named token.txt
    token = None
    try:
        with open('token.txt', 'r') as f:
            token = f.read()
    except IOError:
        pass
    return token

def get_highest_issue_number(repo):
    latest_issue = list(repo.get_issues(state='all', since=datetime.datetime(2022, 5, 1), direction='desc'))
    return latest_issue[0].number

def find_all_mentions(text):
    REGEX_STRING = '(?:\/jekyll\/jekyll-admin\/)(?:issues|pull)+\/(\d+)'
    REGEX_NUMBER_STRING = '(?<=#)\d+'
    regex_matches = []
    regex_matches += [x.group(1) for x in re.finditer(REGEX_STRING, text)]
    regex_matches += re.findall(REGEX_NUMBER_STRING, text)
    return regex_matches


g = Github(get_token())
graph_dict = {}
repo = g.get_repo(TARGET_REPO)

for issue_number in range(199, get_highest_issue_number(repo)):
    try:
        item = repo.get_issue(issue_number)
        total_links = []

        if (item.user.type != 'Bot'):
            total_links += find_all_mentions(item.body)

        for comment in item.get_comments():
            if (comment.user.type != 'Bot'):
                total_links += find_all_mentions(comment.body)
        graph_dict.update({issue_number: total_links})
        print({issue_number: total_links})

    except Exception as e:
        print('')

with open('graph.txt', 'w') as f:
    f.write(json.dumps(graph_dict, sort_keys=True, indent=4))



