import datetime
import re
from github import Github
import picklereader
import networkx as nx
import json
import os

class VisCreator(picklereader.PickleReader):
    def __init__(self, github_token, target_repo_list):
        self.g = Github(github_token)
        self.target_repo_list = target_repo_list
        self.component_id = 0
    
    def create_vis_for_all_repo(self):
        for target_repo in self.target_repo_list:
            graph_dict = self.create_vis_json_for_repo(target_repo)
            self.write_json_to_file(graph_dict, target_repo)
    
    def write_json_to_file(self, graph_dict, target_repo):
        target_repo_no_slash = target_repo.replace('/', '-')
        PATH_FROM_PARENT_DIR = f'raw_data/nodes_{target_repo_no_slash}'
        PATH = os.path.abspath('..')
        with open(f'{PATH}/data/graph_{target_repo_no_slash}.json', 'w') as f:
            f.write(json.dumps(graph_dict, sort_keys=False, indent=4))
        print(f'Saved result to data/graph_{target_repo_no_slash}.json')

    def create_vis_json_for_repo(self, target_repo):
        repo = self.g.get_repo(target_repo)
        repo_contributor_count = repo.get_contributors().totalCount
        nodes, node_list, comment_list, timeline_list, review_comment_list = self.read_repo_local_file(repo, target_repo)
        network_graph = nx.Graph()
        issue_timeline = []

        graph_dict = {
            'repo_url': repo.html_url,
            'issue_count': 0,
            'pull_request_count': 0,
            'labels_text': list(map(lambda x: x.name, list(repo.get_labels()))),
            'nodes': [],
            'links': [],
            'graph_density': 0,
            'graph_node_count': 0,
            'graph_edge_count': 0,
            'graph_component_count': 0,
            'graph_fixes_relationship_count': 0,
            'graph_duplicate_relationship_count': 0,
        }
        fixes_relationship_counter = 0
        duplicate_relationship_counter = 0

        # First, we populate the nodes array as required by D3
        for index, issue in enumerate(nodes):
            # node_dict is the dictionary that specifies a node in D3 network graph
            node_dict = {
                'id': issue.number, # required field 
                'type': 'pull_request' if issue.pull_request is not None else 'issue', # shape of the node
                'status': issue.state, # colour of the node
                'label': list(map(lambda x: x.name, issue.labels)), # filtering feature, filter by issue label
                'creation_date': issue.created_at.timestamp(), # used for temporal aspect 
                'closed_at': issue.closed_at.timestamp() if issue.closed_at is not None else 0, # used for temporal aspect
                'updated_at': issue.updated_at.timestamp(), # used for temporal aspect
                'comments': int(issue.comments), # number of comments in node 
                'repo_contributors': repo_contributor_count, 
                'node_creator': issue.user.html_url # url to the author of the issue
            }
            if issue.pull_request is not None:
                # this ugly check is needed to find out whether a PR is merged
                # since PyGithub doesn't support this directly
                if issue.pull_request.raw_data['merged_at'] is not None:
                    node_dict['status'] = 'merged'
            graph_dict['nodes'].append(node_dict)
            network_graph.add_node(issue.number)

            issue_timeline = list(filter(lambda x: x.event == 'cross-referenced' and x.source.issue.repository.full_name == repo.full_name, issue_timeline))
            issue_timeline_events = issue_timeline.copy()
            issue_timeline_timestamp = issue_timeline.copy()
            issue_timeline_timestamp = list(map(lambda x: x.created_at, issue_timeline_timestamp))

            links_dict = []
            for mention in issue_timeline_events:
                # Tracks INCOMING MENTIONS
                if hasattr(mention.event.actor, 'type'):
                    if mention.event.actor.type == 'Bot':
                        continue

                mentioning_issue = mention.source.issue
                mentioning_issue_comments = self.find_comment(mentioning_issue.url, comment_list)
                mentioning_time = mention.created_at

                target_issue_number = issue.number

                mentioning_issue_reviews = []

                for review_comment in review_comment_list:
                    if self.find_review_url(review_comment) == issue.url:
                        mentioning_issue_reviews.append(review_comment)
                    
                    comment_link, comment_text = self.find_link_and_text_of_comment(target_repo, target_issue_number, mentioning_issue, mentioning_issue_comments, mentioning_issue_reviews, mentioning_time)

                    link_type = self.find_automatic_links(issue.number, mentioning_issue.body, mentioning_issue_comments)
                    if link_type == 'fixes':
                        fixes_relationship_counter += 1
                    elif link_type == 'duplicate':
                        duplicate_relationship_counter += 1

                    links_dict.append({
                            'number': mention.source.issue.number,
                            'comment_link': comment_link,
                            'comment_text': comment_text,
                            'link_type': self.find_automatic_links(issue.number, mentioning_issue.body, mentioning_issue_comments),
                        })
            for link in links_dict:
                # add link to D3 links dict
                graph_dict['links'].append({
                    'source': link['number'], 
                    'target': issue.number, 
                    'comment_link': link['comment_link'],
                    'comment_text': link['comment_text'],
                    'link_type': link['link_type'],
                })
                network_graph.add_edge(link['number'], issue.number)
        connected_components = list(nx.connected_components(network_graph))
        node_count = len(list(network_graph.nodes))
        edge_count = len(list(network_graph.edges))
        graph_dict['graph_component_count'] = len(connected_components)
        graph_dict['graph_node_count'] = node_count
        graph_dict['graph_edge_count'] = edge_count
        graph_dict['graph_density'] = edge_count / ((node_count * (node_count - 1)) / 2)
        graph_dict['graph_fixes_relationship_count'] = fixes_relationship_counter
        graph_dict['graph_duplicate_relationship_count'] = duplicate_relationship_counter

        for component in connected_components:
            for node in component:
                for entry in graph_dict['nodes']:
                    if (entry['id'] == node):
                        entry['connected_component'] = list(component)
                        entry['connected_component_size'] = len(list(component))
                        entry['component_id'] = self.component_id
            self.component_id += 1
        
        for node in network_graph.degree:
            node_id = node[0]
            node_degree = node[1]
            for entry in graph_dict['nodes']:
                if (entry['id'] == node_id):
                    entry['node_degree'] = node_degree
        graph_dict['connected_components'] = list(map(lambda x: list(x), connected_components))

        return graph_dict

    def find_automatic_links(issue_number, issue_body, comments):
        if issue_body is None:
            issue_body = ''
        if comments is None:
            comments = []
        REGEX_STRING = f'(close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved) #{issue_number}'
        REGEX_DUPLICATE_STRING = f'Duplicate of #{issue_number}'

        match = re.search(REGEX_STRING, issue_body, re.IGNORECASE)
        match_duplicate = re.search(REGEX_DUPLICATE_STRING, issue_body, re.IGNORECASE)
        if match:
            return 'fixes'
        elif match_duplicate:
            return 'duplicate'
        for comment in comments:
            if re.search(REGEX_STRING, comment.body, re.IGNORECASE):
                return 'fixes'
            elif re.search(REGEX_DUPLICATE_STRING, comment.body, re.IGNORECASE):
                return 'duplicate'
        return 'other'

    def find_review_url(review_comment):
        if hasattr(review_comment, 'issue_url'):
            return review_comment.issue_url.replace('/pulls/', '/issues/')
        elif hasattr(review_comment, 'pull_request_url'):
            return review_comment.pull_request_url.replace('/pulls/', '/issues/')
        return None # Github do be like that sometimes, where we just cant find the URL

    def find_comment(issue_url, comment_list):
        for comments in comment_list:
            if len(comments) > 0 and comments[0].issue_url == issue_url:
                return comments

    def time_matches(timestamp, tolerance_time):
        return (tolerance_time - datetime.timedelta(seconds=1)) <= timestamp <= (tolerance_time + datetime.timedelta(seconds=1))

    def find_link_and_text_of_comment(self, TARGET_REPO, target_issue_number, issue, comments, review_comments, timestamp):
        if self.time_matches(timestamp, issue.created_at) or self.time_matches(timestamp, issue.updated_at):
            return f'{issue.html_url}#issue-{issue.id}', issue.body
        if comments is not None:
            for comment in comments:
                if timestamp - datetime.timedelta(seconds=3) <= comment.created_at <= timestamp + datetime.timedelta(seconds=3):
                    return comment.html_url, comment.body
        # at this point, we still have not identified the link
        # We will manually use regex at this point
        REGEX_STRING = f'#{target_issue_number}'
        REGEX_STRING_URL = f'https:\/\/github\.com/{TARGET_REPO}\/(?:issues|pull)\/{target_issue_number}'
        # Search all the comments in the node with the mention
        if comments is not None:
            for comment in comments:
                if re.search(REGEX_STRING, comment.body) or re.search(REGEX_STRING_URL, comment.body) is not None:
                    return comment.html_url, comment.body
        if review_comments is not None:
            for comment in review_comments:
                if re.search(REGEX_STRING, comment.body) or re.search(REGEX_STRING_URL, comment.body) is not None:
                    return comment.html_url, comment.body
        # Search the body text of the node itself
        if issue.body is not None:
            if re.search(REGEX_STRING, issue.body) or re.search(REGEX_STRING_URL, issue.body) is not None:
                return f'{issue.html_url}#issue-{issue.id}', issue.body
        return None, ''