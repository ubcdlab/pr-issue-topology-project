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

RATE_LIMIT_THRESHOLD = 100

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


def find_link_to_comment(issue, comments, timestamp):
    if time_matches(timestamp, issue.created_at) or time_matches(timestamp, issue.updated_at):
        return f'{issue.html_url}#issue-{issue.id}'
    if comments is not None:
        for comment in comments:
            if timestamp - datetime.timedelta(seconds=1) <= comment.created_at <= timestamp + datetime.timedelta(seconds=1):
                return comment.html_url
    return f'{issue.html_url}'

def time_matches(timestamp, tolerance_time):
    return (tolerance_time - datetime.timedelta(seconds=1)) <= timestamp <= (tolerance_time + datetime.timedelta(seconds=1))

def delete_saved_files():
    PATH = f'raw_data/nodes_{TARGET_REPO_FILE_NAME}'
    confirmation = input('Confirm the removal of saved progress files? ')
    if confirmation != 'y':
        print('Abort')
        return
    print('Removing saved progress files...')
    with contextlib.suppress(FileNotFoundError):
        os.remove(f'{PATH}.pk')
        os.remove(f'{PATH}_comments.pk')
        os.remove(f'{PATH}_progress.pk')
        os.remove(f'{PATH}_event.pk')

def write_variables_to_file(nodes, node_list, comment_list, timeline_list, TARGET_REPO_FILE_NAME):
    PATH = f'raw_data/nodes_{TARGET_REPO_FILE_NAME}'
    print('Writing raw nodes and comment data to disk...\nDO NOT INTERRUPT OR TURN OFF YOUR COMPUTER.')

    with open(f'{PATH}.pk', 'wb') as fi:
        pickle.dump(nodes, fi)
    with open(f'{PATH}_progress.pk', 'wb') as fi:
        pickle.dump(node_list, fi)
    with open(f'{PATH}_comments.pk', 'wb') as fi:
        pickle.dump(comment_list, fi)
    with open(f'{PATH}_event.pk', 'wb') as fi:
        pickle.dump(timeline_list, fi)

def write_json_to_file(graph_dict, TARGET_REPO_FILE_NAME):
    with open(f'data/graph_{TARGET_REPO_FILE_NAME}.json', 'w') as f:
        f.write(json.dumps(graph_dict, sort_keys=False, indent=4))
    print(f'Saved result to data/graph_{TARGET_REPO_FILE_NAME}.json')

def check_rate_limit(rate_limit, RATE_LIMIT_THRESHOLD, nodes, node_list, comment_list, timeline_list, TARGET_REPO_FILE_NAME):
    if rate_limit.core.remaining < RATE_LIMIT_THRESHOLD:
        print('Rate limit threshold reached!')
        time_remaining = rate_limit.core.reset - datetime.datetime.utcnow()
        print(f'Rate limit will reset after {time_remaining.seconds // 60} minutes {time_remaining.seconds % 60} seconds')
        print(f'Rate limit reset time: {rate_limit.core.reset}' ) # I am not going to bother figuring out printing local time 
        print(f'Sleeping for {time_remaining.seconds + 5} seconds.')
        write_variables_to_file(nodes, node_list, comment_list, timeline_list, TARGET_REPO_FILE_NAME)
        time.sleep(time_remaining.seconds + 5)
        # raise Exception('RateLimitThreshold')

def load_saved_progress(repo, TARGET_REPO_FILE_NAME):
    PATH = f'raw_data/nodes_{TARGET_REPO_FILE_NAME}'

    nodes = []
    node_list = []
    comment_list = []
    timeline_list = []

    if exists(f'{PATH}.pk') is True:
        with open(f'{PATH}.pk', 'rb') as fi:
            nodes = pickle.load(fi)
    else:
        nodes = list(repo.get_issues(state='all', sort='created', direction='desc'))
        node_list = nodes.copy()

    if exists(f'{PATH}_comments.pk') is True:
        with open(f'{PATH}_comments.pk', 'rb') as fi:
            comment_list = pickle.load(fi)
    if exists(f'{PATH}_progress.pk') is True:
        with open(f'{PATH}_progress.pk', 'rb') as fi:
            node_list = pickle.load(fi)
    if exists(f'{PATH}_event.pk') is True:
        with open(f'{PATH}_event.pk', 'rb') as fi:
            timeline_list = pickle.load(fi)

    return nodes, node_list, comment_list, timeline_list

def get_data(g, TARGET_REPO, TARGET_REPO_FILE_NAME):
    # Remember, the ONLY RESPONSIBILITY OF THIS FUNCTION
    # IS TO DOWNLOAD THE DATA, NO FILTERING, NO PROCESSING
    repo = g.get_repo(TARGET_REPO)

    print(f'Downloading repo: {repo.html_url} with {repo.open_issues} open issues')

    nodes, node_list, comment_list, timeline_list = load_saved_progress(repo, TARGET_REPO_FILE_NAME)    

    if (len(nodes) > 0 and len(comment_list) > 0) and len(nodes) == len(comment_list):
        # Already done, just return the results loaded from file
        print('All nodes has already been downloaded and processed. Skipping download and loading saved local files.')
        return nodes, comment_list, timeline_list
    else:
        # Download the remaining nodes
        print(f'Nodes remaining to load from repo: {len(node_list)}')
        try:
            while len(node_list) > 0:
                check_rate_limit(g.get_rate_limit(), RATE_LIMIT_THRESHOLD, nodes, node_list, comment_list, timeline_list, TARGET_REPO_FILE_NAME)
                issue = node_list[-1]
                # issue = node_list.pop(0)
                node_comments = issue.get_comments()
                node_timeline = issue.get_timeline()
                timeline_list.append(list(node_timeline))
                comment_list.append(list(node_comments))

                node_list.pop()
                print(f'Downloaded node {issue.number}. {len(node_list)} remaining. Rate limit: {g.rate_limiting[0]}')
        except Exception as e:
            # Need to wait for rate limit cooldown
            print(e)
            # print('Halting download due to rate limit...')
            write_variables_to_file(nodes, node_list, comment_list, timeline_list, TARGET_REPO_FILE_NAME)
            sys.exit(0) # abort the download process
        
        # We made it through downloading the whole thing with no rate limit incident
        # Save the full progress
        write_variables_to_file(nodes, node_list, comment_list, timeline_list, TARGET_REPO_FILE_NAME)
        g.get_rate_limit()
        print(f'Finished downloading entire repo. Rate limit: {g.rate_limiting[0]}')
        return nodes, comment_list, timeline_list # return the result

def find_comment(issue_url, comment_list):
    for comments in comment_list:
        if len(comments) > 0 and comments[0].issue_url == issue_url:
            return comments

def get_event_date(event):
    # HACK: to get around Github repo's psychopathic behaviour
    result = event.created_at
    if result is not None:
        return result
    if 'author' in event.raw_data:
        # this usually works for event.event == 'commit'
        result = event.raw_data['author']['date']
    if result is not None:
        return result
    if 'user' in event.raw_data:
        # this usually works for event.event == 'commented'
        if event.raw_data['submitted_at'] is not None:
            result = event.raw_data['submitted_at']
    if result is not None:
        return result
    if event.raw_data['comments'][0] is not None:
        # this usually works for event.event == 'commit-commented"
        result = event.raw_data['comments'][0]['created_at']
    if result is not None:
        return result
    
    assert(1 == 0)
    return event.raw_data['author']['date']

def create_json(g, nodes, comment_list, timeline_list, TARGET_REPO_FILE_NAME):
    repo = g.get_repo(TARGET_REPO)
    network_graph = nx.Graph()
    
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

    nonwork_events = ['subscribed', 'unsubscribed', 'automatic_base_change_failed', 'automatic_base_change_succeeded']

    for index, issue in enumerate(nodes):
        node_dict = {}
        # node_comments = find_comment(issue.url, comment_list)
        # NOTE: node_comments remains currently unused, but in case we'll need it in the future
        # I am keeping the code commented here

        # HACK: horrible hack to remedy a problem
        # nodes are loaded in ascending order
        # yet timeline_list is loaded in descending order
        issue_timeline = timeline_list[-index-1]

        issue_commit_timeline_2 = []
        issue_commit_timeline = issue_timeline.copy()
        issue_commit_timeline = list(filter(lambda x: x.event not in nonwork_events, issue_commit_timeline))
        for event in issue_commit_timeline:
            # NOTE: events of type 'commit' have no actor.url... in fact
            # a lot of the fields aren't set... 
            # TODO: FIX THIS... USE THE DEBUGGER
            # some Github timeline events just dont have event ID for some cursed reason
            # these are usually commit events
            event_type = event.event
            event_time = get_event_date(event)
            # print(f'{event.actor.url}\n{event.created_at}')
            print(f'{event_type}: {event_time}')
            issue_commit_timeline_2.append({
                'event': event.event,
                'created_at': event.created_at
            })
        issue_commit_timeline = list(map(lambda x: x.url, issue_commit_timeline))
        # print(issue_commit_timeline)

        issue_timeline = list(filter(lambda x: x.event == 'cross-referenced' and x.source.issue.repository.full_name == repo.full_name, issue_timeline))
        issue_timeline_events = issue_timeline.copy()
        issue_timeline_timestamp = issue_timeline.copy()
        issue_timeline_timestamp = list(map(lambda x: x.created_at, issue_timeline_timestamp))

        links_dict = []
        for mention in issue_timeline_events:
            # Tracks INCOMING MENTIONS
            mentioning_issue = mention.source.issue
            mentioning_issue_comments = find_comment(mentioning_issue.url, comment_list)
            mentioning_time = mention.created_at
            
            comment_link = find_link_to_comment(mentioning_issue, mentioning_issue_comments, mentioning_time)
            assert comment_link is not None

            link_type = find_automatic_links(issue.number, mentioning_issue.body, mentioning_issue_comments)
            if link_type == 'fixes':
                fixes_relationship_counter += 1
            elif link_type == 'duplicate':
                duplicate_relationship_counter += 1

            links_dict.append({
                    'number': mention.source.issue.number,
                    'comment_link': comment_link,
                    'link_type': find_automatic_links(issue.number, mentioning_issue.body, mentioning_issue_comments)
                })
        node_dict = {
            'id': issue.number,
            'type': 'pull_request' if issue.pull_request is not None else 'issue',
            'status': issue.state,
            'links': links_dict,
            'label': list(map(lambda x: x.name, issue.labels)),
            'creation_date': issue.created_at.timestamp(),
            'closed_at': issue.closed_at.timestamp() if issue.closed_at is not None else 0,
            'updated_at': issue.updated_at.timestamp(),
            'event_list': issue_commit_timeline
        }

        if issue.pull_request is not None:
            # this ugly check is needed to find out whether a PR is merged
            # since PyGithub doesn't support this directly
            if issue.pull_request.raw_data['merged_at'] is not None:
                node_dict['status'] = 'merged'
        graph_dict['nodes'].append(node_dict)
        network_graph.add_node(issue.number)
        for link in links_dict:
            graph_dict['links'].append({
                'source': link['number'], 
                'target': issue.number, 
                'comment_link': link['comment_link'],
                'link_type': link['link_type'] 
                })
            network_graph.add_edge(link['number'], issue.number)
        print(f'Finished processing node number {issue.number}')
    # Finished loading all nodes
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
                    entry['connected_component_size'] = [len(list(component))]
    
    for node in network_graph.degree:
        node_id = node[0]
        node_degree = node[1]
        for entry in graph_dict['nodes']:
            if (entry['id'] == node_id):
                entry['node_degree'] = node_degree
    graph_dict['connected_components'] = list(map(lambda x: list(x), connected_components))
    return graph_dict

try:
    TARGET_REPO = sys.argv[1]
    TARGET_REPO_FILE_NAME = TARGET_REPO.replace('/', '-')
except IndexError:
    print(f'Expected at least 1 argument, found {len(sys.argv) - 1}')
    print('Exiting')
    sys.exit(1)

if ('reload' in sys.argv) is True:
    delete_saved_files()

g = Github(get_token())
nodes, comment_list, timeline_list = get_data(g, TARGET_REPO, TARGET_REPO_FILE_NAME)
graph_dict = create_json(g, nodes, comment_list, timeline_list, TARGET_REPO_FILE_NAME)
write_json_to_file(graph_dict, TARGET_REPO_FILE_NAME)



