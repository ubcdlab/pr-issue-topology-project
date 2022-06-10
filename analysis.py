import json
import sys 

f = open('data/graph.json')
data = json.load(f)
pattern_json = {}

isolated = []
duo_issue_issue = []
duo_issue_pr = []
duo_pr_pr = []
duo_pr_issue = []
counter = 0

def find_node(node_id):
	for node in data['nodes']:
		if node['id'] == node_id:
			return node

def compute_node_order(source_node, sink_node):
	return [source_node['type'], sink_node['type']]

# First, find isolated nodes
for component in data['connected_components']:
	if len(component) == 1:
		isolated.append(component)

pattern_json['isolated'] = isolated

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

pattern_json['duo_issue_issue'] = duo_issue_issue
pattern_json['duo_issue_pr'] = duo_issue_pr
pattern_json['duo_pr_pr'] = duo_pr_pr
pattern_json['duo_pr_issue'] = duo_pr_issue

print(len(duo_issue_issue) + len(duo_issue_pr) + len(duo_pr_pr) + len(duo_pr_issue))
print(counter)

with open('data/structure.json', 'w') as f:
	f.write(json.dumps(pattern_json, sort_keys=False, indent=4))

# print(pattern_json)