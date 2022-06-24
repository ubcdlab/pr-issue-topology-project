from github import Github
import datetime
import re
import sys
import json
import pickle


nodes = None
with open('nodes.pk', 'rb') as fi:
	nodes = pickle.load(fi)

print(nodes)