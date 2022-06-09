from github import Github
import traceback
import datetime
import re
import sys
import json
import networkx as nx

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
    latest_issue = list(repo.get_issues(state='all', direction='desc'))
    return latest_issue[0].number

def find_all_mentions(text):
    ''' 
    Github is pathological; mentions to other issues/PR
    sometimes shows up as a string literal of form '#{NUMBER}'
    and sometimes shows up as a string URL of form 'https://github.com/[REPO URL]/{pull/issue}/{NUMBER}'

    Therefore, two seperate regex are required to properly detect mentions
    and even then, I am not 100% confident about this method's accuracy
    '''

    REGEX_STRING = '(?:issues|pull)+\/(\d+)'
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

def fetch_data(target_organization):
    if target_organization is None:
        print('No org URL given; defaulting to cpsc310-2020w-t1')
        target_organization = 'cpsc310-2020w-t1'
    token = get_token()
    graph_dict = {}
    g = Github(base_url='https://github.students.cs.ubc.ca/api/v3', login_or_token=str(token))
    org = g.get_organization(target_organization)
    repo_collection = list(org.get_repos())
    graph_dict['org_url'] = org.url
    graph_dict['issue_count'] = 0
    graph_dict['pull_request_count'] = 0
    graph_dict['links'] = 0
    graph_dict['repo_count'] = len(repo_collection)

    for repo in repo_collection:
        HIGHEST_ISSUE_NUMBER = get_highest_issue_number(repo)
        for issue_number in range(1, HIGHEST_ISSUE_NUMBER + 1):
            # go through every possible issue/PR number
            try:
                item = repo.get_issue(issue_number) # get the issue
                total_links = [] # initialise array of matches, set to empty
                node_dict = {}

                if (item.user.type != 'Bot'): # filter out links/mentions made by bot accounts 
                    total_links += find_all_mentions(item.body) # find all mentions in issue/PR description

                for comment in item.get_comments(): # go through every single comment
                    if (comment.user.type != 'Bot'): # filter out links/mentions made by bot accounts
                        total_links += find_all_mentions(comment.body) # find all mentions in a specific comment
                
                # filter out mentions to other projects, right now we catch mentions
                # to other projects by removing links with an issue/PR number that is higher
                # than the project of concern
                total_links = len(list(filter(lambda x: (int(x) <= HIGHEST_ISSUE_NUMBER), total_links)))

                ''' Github API treats both issue and PR as issues (PRs are issues with code),
                    API docs direct us to distinguish between the two by checking the pull_request key
                    which is None for issues
                '''
                node_dict['id'] = issue_number
                node_dict['type'] = 'pull_request' if item.pull_request is not None else 'issue'
                if item.pull_request is not None:
                    graph_dict['pull_request_count'] = graph_dict['pull_request_count'] + 1
                else:
                    graph_dict['issue_count'] = graph_dict['issue_count'] + 1

                graph_dict['links'] = graph_dict['links'] + total_links

            except Exception as e:
                # Exceptions usually happens, when we try to load a number 
                # that doesn't correspond to an issue or pull request
                # idk why Github let this happens
                print(e)

    print('Finished downloading entire org.')
    return graph_dict

try:
    org_url = sys.argv[1]
except:
    org_url = None
finally:
    result = fetch_data(org_url)

with open('result.json', 'w') as f:
    # save result to disk
    f.write(json.dumps(result, sort_keys=False, indent=4))



