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
    if len(nodes) == len(comment_list):
        # Already done, just return the results loaded from file
        print('All nodes has already been downloaded and processed. Loading saved local files.')
        return nodes, comment_list
    else:
        # Download the remaining nodes
        print(f'Nodes remaining to laod: {len(node_list)}')
        try:
            while len(node_list) > 0:
                if g.get_rate_limit().core.remaining < RATE_LIMIT_THRESHOLD:
                    print('Rate limit threshold reached!')
                    rate_limit_time = g.get_rate_limit()
                    time_remaining = rate_limit_time.core.reset - datetime.datetime.utcnow()
                    print(f'Rate limit will reset after {time_remaining.seconds // 60} minutes {time_remaining.seconds % 60} seconds')
                    print(f'Rate limit reset time: {rate_limit_time.core.reset}' ) # I am not going to bother figuring out printing local time 
                    raise Exception('RateLimitThreshold')
                issue = node_list.pop(0)
                total_links = []
                node_dict = {}

                if (issue.user.type != 'Bot'):
                    total_links += find_all_mentions(issue.body)
                node_comments = issue.get_comments()
                for comment in node_comments:
                    if (comment.user.type != 'Bot'):
                        total_links += find_all_mentions(comment.body)

                total_links = list(filter(lambda x: (0 < int(x) <= HIGHEST_ISSUE_NUMBER) and int(x) in issue_and_pr_numbers, total_links))
                # print(total_links)

                node_dict['id'] = issue.number
                node_dict['type'] = 'pull_request' if issue.pull_request is not None else 'issue'
                node_dict['status'] = issue.state
                node_dict['links'] = total_links

                if issue.pull_request is not None:
                    # this ugly check is needed to find out whether a PR is merged
                    # since PyGithub doesn't support this directly
                    if issue.pull_request.raw_data['merged_at'] is not None:
                        node_dict['status'] = 'merged'

                graph_dict['nodes'].append(node_dict)
                for link in total_links:
                    graph_dict['links'].append({'source': issue.number, 'target': int(link)})

                print(f'Finished processing node {issue.number}. Rate limit: {g.rate_limiting[0]}')
                # node_list.remove(issue)
                comment_list.append(list(node_comments))
        except Exception as e:
            # Need to wait for rate limit cooldown
            print(e)
            print('Halting download due to rate limit...')
            print('Writing raw nodes and comment data to disk... ')
            print('DO NOT INTERRUPT OR TURN OFF YOUR COMPUTER.')
            with open(f'raw_data/nodes_{TARGET_REPO_FILE_NAME}_progress.pk', 'wb') as fi:
                pickle.dump(node_list, fi)
            with open(f'raw_data/nodes_{TARGET_REPO_FILE_NAME}_comments.pk', 'wb') as cfi:
                pickle.dump(comment_list, cfi)
            sys.exit(0) # abort the download process
        
        # We made it through downloading the whole thing with no rate limit incident
        # Save the full progress
        print('Writing raw nodes and comment data to disk... ')
        print('DO NOT INTERRUPT OR TURN OFF YOUR COMPUTER.')
        with open(f'raw_data/nodes_{TARGET_REPO_FILE_NAME}_progress.pk', 'wb') as fi:
            pickle.dump(node_list, fi)
        with open(f'raw_data/nodes_{TARGET_REPO_FILE_NAME}_comments.pk', 'wb') as cfi:
            pickle.dump(comment_list, cfi)
        g.get_rate_limit()
        print(f'Finished downloading entire repo. Rate limit: {g.rate_limiting[0]}')
        # return the result
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
