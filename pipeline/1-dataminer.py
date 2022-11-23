from inspect import Attribute
from xmlrpc.client import DateTime
from github import Github
import datetime
import re
import sys
import json
import networkx as nx
import pickle
from os.path import exists
import os
import time
import contextlib
from dateutil import parser

class Dataminer(object):
    def __init__(self, github_token, target_repo_list):
        self.g = Github(github_token)
        self.target_repo_list = target_repo_list

    def load_saved_progress(self, repo, target_repo):
        PATH = f'./../raw_data/nodes_{target_repo}'
        nodes, node_list, comment_list, timeline_list, review_comment_list = ([] for i in range(5))
        try:
            nodes = pickle.load(open(f'{PATH}.pk', 'rb'))
            node_list = pickle.load(open(f'{PATH}_progress.pk', 'rb'))
            comment_list = pickle.load(open(f'{PATH}_comments.pk', 'rb'))
            timeline_list = pickle.load(open(f'{PATH}_event.pk', 'rb'))
            review_comment_list = pickle.load(open(f'{PATH}_review_comments.pk', 'rb'))
        except:
            nodes = list(repo.get_issues(state='all', sort='created', direction='desc'))
            node_list = nodes.copy()
            review_comment_list = list(repo.get_pulls_review_comments(sort='created', direction='desc'))
            pickle.dump(review_comment_list, open(f'{PATH}_review_comments.pk', 'wb'))
        return nodes, node_list, comment_list, timeline_list, review_comment_list
    
    def download_all_repo_data(self):
        for target_repo in self.target_repo_list:
            repo = self.g.get_repo()

    def download_repo_data(self, target_repo):
        repo = self.g.get_repo(target_repo)

        print(f'Downloading repo: {repo.html_url} with {repo.open_issues} open issues')

        nodes, node_list, comment_list, timeline_list, review_comment_list = self.load_saved_progress(repo, target_repo)



    