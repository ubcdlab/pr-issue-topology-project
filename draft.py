def get_data():
    g = Github(get_token())
    graph_dict = {}
    
    repo = g.get_repo(TARGET_REPO)
    repo_url = repo.html_url

    nodes = None
    comment_list = []

    print(f'Downloading repo: {repo_url} with {repo.open_issues} open issues')

    node_post_file_exist = exists(f'raw_data/nodes_{TARGET_REPO_FILE_NAME}.pk')
    if node_post_file_exist is True:
        print('Already crawled repo before, loading save file')
        with open(f'raw_data/nodes_{TARGET_REPO_FILE_NAME}.pk', 'rb') as fi:
            nodes = pickle.load(fi)
    else:
        print('Never crawled repo before, creating save file')
        nodes = list(repo.get_issues(state='all', sort='created', direction='desc'))

    print(f'Loaded {len(nodes)} nodes from repo.')

    node_progress_file_exist = exists(f'raw_data/nodes_{TARGET_REPO_FILE_NAME}_comments.pk')

    if node_progress_file_exist is True:
        # we aren't startin from scratch
        print('Already crawled comments before, loading save file')
        with open(f'raw_data/nodes_{TARGET_REPO_FILE_NAME}_progress.pk', 'rb') as fi:
            node_list = pickle.load(fi)
        with open(f'raw_data/nodes_{TARGET_REPO_FILE_NAME}_comments.pk', 'rb') as fi:
            comment_list = pickle.load(fi)
    else:
        # we never crawled this repo before
        print('Never crawled comments before, creating save file')
        with open(f'raw_data/nodes_{TARGET_REPO_FILE_NAME}.pk', 'rb') as npf:
            node_list = pickle.load(npf)
    print(f'Loaded {len(comment_list)} comment nodes.')
    return nodes, comment_list

def dump_to_file():
    graph_dict = {
        'repo_url': repo.html_url,
        'issue_count': 0,
        'pull_request_count': 0,
        'labels_text': list(map(lambda x: x.name, list(repo.get_labels()))),
        'nodes': [],
        'links': []
    }
    HIGHEST_ISSUE_NUMBER = nodes[0].number
    for index, issue in enumerate(nodes):
        total_links = []
        node_dict = {}

        node_comments = comment_list[index]

        issue_timeline = list(issue.get_timeline())
        issue_timeline = list(filter(lambda x: x.event == 'cross-referenced' and x.source.issue.repository.full_name == repo.full_name , issue_timeline))
        issue_timeline_timestamp = copy.deepcopy(issue_timeline)
        issue_timeline_timestamp = list(map(lambda x: x.created_at, issue_timeline_timestamp))
        issue_timeline_events = copy.deepcopy(issue_timeline)
        issue_timeline = list(map(lambda x: str(x.source.issue.number), issue_timeline))

        total_links = issue_timeline

        links_dict = []

        for mention in issue_timeline_events:
            mentioning_issue = mention.source.issue
            mentioning_issue_comments = mentioning_issue.get_comments()
            mentioning_time = mention.created_at
            comment_link = find_link_to_comment(mentioning_issue, mentioning_issue_comments, mentioning_time)
            assert comment_link is not None
            links_dict.append({
                    'number': mention.source.issue.number,
                    'comment_link': comment_link
                })

        node_dict = {
            'id': issue.number,
            'type': 'pull_request' if issue.pull_request is not None else 'issue',
            'status': issue.state,
            'links': links_dict,
            'label': list(map(lambda x: x.name, issue.labels))
        }

        if issue.pull_request is not None:
            # this ugly check is needed to find out whether a PR is merged
            # since PyGithub doesn't support this directly
            if issue.pull_request.raw_data['merged_at'] is not None:
                node_dict['status'] = 'merged'

        graph_dict['nodes'].append(node_dict)
        for link in links_dict:
            graph_dict['links'].append({'source': link['number'], 'target': issue.number, 'comment_link': link['comment_link']})
        # for link in total_links:
        #     graph_dict['links'].append({'source': int(link), 'target': issue.number, })
        print(f'Finished loading node number {issue.number}')
    graph = nx.Graph()
    for node in graph_dict['nodes']:
        graph.add_node(node['id'])
    for link in graph_dict['links']:
        graph.add_edge(link['source'], link['target'])
    connected_components = list(nx.connected_components(graph))

    for component in connected_components:
        for node in component:
            for entry in graph_dict['nodes']:
                if (entry['id'] == node):
                    entry['connected_component'] = list(component)
                    entry['connected_component_size'] = [len(list(component))]

    for node in graph.degree:
        node_id = node[0]
        node_degree = node[1]
        for entry in graph_dict['nodes']:
            if (entry['id'] == node_id):
                entry['node_degree'] = node_degree
    graph_dict['connected_components'] = list(map(lambda x: list(x), connected_components))
    return graph_dict
