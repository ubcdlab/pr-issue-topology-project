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

def remove_hashtag(regex_findall):
    return list(map(lambda x: x[1:], regex_findall))


g = Github(get_token())
graph_dict = {}
repo = g.get_repo(TARGET_REPO)

for issue_number in range(1, get_highest_issue_number(repo)):
    try:
        item = repo.get_issue(issue_number)
        total_links = []
        regex_matches = re.findall('#[0-9]+', item.body)
        if (item.user.type != 'Bot'):
            total_links = total_links + remove_hashtag(regex_matches)
        for comment in item.get_comments():
            regex_matches = re.findall('#[0-9]+', comment.body)
            if (comment.user.type != 'Bot'):
                total_links = total_links + remove_hashtag(regex_matches)
        graph_dict.update({issue_number: total_links})

    except Exception as e:
        print(e)

with open('graph.txt', 'w') as f:
    f.write(json.dumps(graph_dict, sort_keys=True, indent=4))



