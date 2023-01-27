import json
import sys 
import pickle
import networkx as nx

node_list = None
comment_list = None


TARGET_REPO = sys.argv[1]
TARGET_REPO_FILE_NAME = TARGET_REPO.replace('/', '-')

with open(f'raw_data/nodes_{TARGET_REPO_FILE_NAME}_comments.pk', 'rb') as fi:
    comment_list = pickle.load(fi)
with open(f'raw_data/nodes_{TARGET_REPO_FILE_NAME}.pk', 'rb') as fi:
    node_list = pickle.load(fi)


def init_output_json(g, repo):
	# return an initialised graph_{REPO_NAME}.json file
	labels = list(repo.get_labels())
	output = {
		'repo_url': repo.html_url,
		'issue_count': 0,
		'pull_request_count': 0,
		'labels_text': list(map(lambda x: x.name, labels)),
		'nodes': [],
		'links': []
	}
	return output

def compute_network_statistics(data):
    # Construct the graph
    graph = nx.Graph()
    for node in data['nodes']:
        graph.add_node(node['id'])
    for link in data['links']:
        graph.add_edge(link['source'], link['target'])

    # Compute the connected component
    connected_components = list(nx.connected_components(graph))
    for component in connected_components:
        for node in component:
            for entry in data['nodes']:
                if (entry['id'] == node):
                    entry['connected_component'] = list(component)

    # Compute the degrees
    for node in graph.degree:
        node_id = node[0]
        node_degree = node[1]
        for entry in data['nodes']:
            if (entry['id'] == node_id):
                entry['node_degree'] = node_degree
    data['connected_components'] = list(map(lambda x: list(x), connected_components))
    return data

def find_node(node_id):
	for node in data['nodes']:
		if node['id'] == node_id:
			return node

def compute_node_order(source_node, sink_node):
	return [source_node['type'], sink_node['type']]

def add_analysis_function(analysis_dict, level, array_of_function):
	analysis_dict['input'][level][level] = array_of_function

def find_isolated_nodes(node):
	return len(node['connected_components']) == 0

target = node_list[0]

data = None
with open(f'data/graph_{TARGET_REPO_FILE_NAME}.json', 'r') as fi:
    data = json.load(fi)

pattern_json = {}
analysis_dict = {}
isolated = []
duo_issue_issue = []
duo_issue_pr = []
duo_pr_pr = []
duo_pr_issue = []
counter = 0

# First, compute the largest component size
max_component_size = 0
for component in data['connected_components']:
	max_component_size = max(len(component), max_component_size)
# generate the dict for analysis
analysis_dict['input'] = [{0: []}]
for counter in range(1, max_component_size + 1):
	analysis_dict['input'].append({
		counter: []
	})

# Modify the lines below to add custom analysis


# First, find isolated nodes
for component in data['connected_components']:
	if len(component) == 1:
		isolated.append(component)


for component_size in range(1, max_component_size + 1):
	pattern_json[component_size] = {}

'''
A node has form:
id, type, status, links, connected_component, node_degree
'''


# Second, find all possible permutations of duo nodes
for component in data['connected_components']:
	if len(component) != 2:
		continue
	counter += 1
	component.sort()
	lower_number_node = find_node(component[0])
	higher_number_node = find_node(component[1])

	source_node = None
	sink_node = None

	if lower_number_node is None:
		continue

	if len(lower_number_node['links']) == 0:
		sink_node = lower_number_node
		source_node = higher_number_node
	else:
		sink_node = higher_number_node
		source_node = lower_number_node

	ordering = compute_node_order(source_node, sink_node)
	if ordering == ['issue', 'issue']:
		duo_issue_issue.append([source_node, sink_node])
	elif ordering == ['issue', 'pull_request']:
		duo_issue_pr.append([source_node, sink_node])
	elif ordering == ['pull_request', 'pull_request']:
		duo_pr_pr.append([source_node, sink_node])
	elif ordering == ['pull_request', 'issue']:
		duo_pr_issue.append([source_node, sink_node])

pattern_json[1]['isolated'] = isolated
pattern_json[2]['duo_issue_issue'] = duo_issue_issue
pattern_json[2]['duo_issue_pr'] = duo_issue_pr
pattern_json[2]['duo_pr_pr'] = duo_pr_pr
pattern_json[2]['duo_pr_issue'] = duo_pr_issue

for component_size in range(3, max_component_size + 1):
	all_component_of_size = []
	for component in data['connected_components']:
		if len(component) != component_size:
			continue
		a_connected_component = []
		for node in component:
			temp = find_node(node)
			a_connected_component.append(temp)
		all_component_of_size.append(a_connected_component)
	pattern_json[component_size]['general'] = all_component_of_size


with open(f'data/structure_{TARGET_REPO_FILE_NAME}.json', 'w') as f:
	f.write(json.dumps(pattern_json, sort_keys=False, indent=4))

