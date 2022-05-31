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
    ''' 
    Github is pathological; mentions to other issues/PR
    sometimes shows up as a string literal of form '#{NUMBER}'
    and sometimes shows up as a string URL of form 'https://github.com/[REPO URL]/{pull/issue}/{NUMBER}'

    Therefore, two seperate regex are required to properly detect mentions
    and even then, I am not 100% confident about this method's accuracy
    '''

    REGEX_STRING = '(?:\/jekyll\/jekyll-admin\/)(?:issues|pull)+\/(\d+)'
    # the above regex uses non-capturing groups for the repo URLs, so only the number (the part we want)
    # is captured.

    REGEX_NUMBER_STRING = '(?<=#)\d+'
    # the above regex uses positive lookbehind to only capture numbers (the part we want)
    # from the pattern #{NUMBER}

    regex_matches = []
    regex_matches += [x.group(1) for x in re.finditer(REGEX_STRING, text)]
    regex_matches += re.findall(REGEX_NUMBER_STRING, text)
    return regex_matches # return all matches in an array


g = Github(get_token())
graph_dict = {}
repo = g.get_repo(TARGET_REPO)

HIGHEST_ISSUE_NUMBER = get_highest_issue_number(repo)

for issue_number in range(1, HIGHEST_ISSUE_NUMBER):
    # go through every possible issue/PR number
    try:
        item = repo.get_issue(issue_number) # get the issue
        total_links = [] # initialise array of matches, set to empty

        if (item.user.type != 'Bot'): # filter out links/mentions made by bot accounts 
            total_links += find_all_mentions(item.body) # find all mentions in issue/PR description

        for comment in item.get_comments(): # go through every single comment
            if (comment.user.type != 'Bot'): # filter out links/mentions made by bot accounts
                total_links += find_all_mentions(comment.body) # find all mentions in a specific comment
        
        # filter out mentions to other projects, right now we catch mentions
        # to other projects by removing links with an issue/PR number that is higher
        # than the project of concern
        total_links = list(filter(lambda x: (int(x) <= HIGHEST_ISSUE_NUMBER), total_links))

        # update the dictionary storing the graph toplogy 
        graph_dict.update({issue_number: total_links})
        print({issue_number: total_links})

    except Exception as e:
        # Exceptions usually happens, when we try to load a number 
        # that doesn't correspond to an issue or pull request
        # idk why this happens
        print(e)

with open('graph.txt', 'w') as f:
    # save result to disk
    f.write(json.dumps(graph_dict, sort_keys=True, indent=4))



