from github import Github
import datetime

TARGET_REPO = 'jekyll/jekyll-admin'

def get_token():
    # get personal access token
    # from a file named token.txt
    token = None
    try:
        with open('token.txt') as f:
            token = f.read()
    except IOError:
        pass
    return token

g = Github(get_token())

repo = g.get_repo('jekyll/jekyll-admin')

item = repo.get_issue(number=23)
print(item)