from github import Github
import datetime
import picklereader
import sys
import pickle
import time
import os

class VisCreator(picklereader.PickleReader):

    def __init__(self, github_token, target_repo_list):
        self.g = Github(github_token)
        self.target_repo_list = target_repo_list
    
    def create_vis_for_all_repo(self):
        for target_repo in self.target_repo_list:
            self.create_vis_for_repo(target_repo)
    
    def create_vis_for_repo(self):
        return

    def create_vis_json_file(self):
        self.read_repo_local_file()