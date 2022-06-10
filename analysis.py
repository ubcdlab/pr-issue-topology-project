import json 

f = open('data/graph.json')
data = json.load(f)
pattern_json = {}

isolated = []
duo_issue_issue = []
duo_issue_pr = []
duo_pr_pr = []
duo_pr_issue = []

def find_node(node_id):
	for node in data['nodes']:
		if node['id'] == node_id:
			return node


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
for node in data['nodes']:
	if len(node['connected_component']) != 2 or len(node['links']) == 0:
		# ignore sink nodes 
		continue
	current_node = node
	other_node = None
	for constituent_id in node['connected_component']:
		if constituent_id == node:
			continue
		other_node = find_node(constituent_id)
	# Today on mythconfirms, what happens when write bad code?
	if node['type'] == 'issue' and other_node['type'] == 'issue':
		duo_issue_issue.append([node, other_node])
	elif node['type'] == 'issue' and other_node['type'] == 'pull_request':
		duo_issue_pr.append([node, other_node])
	elif node['type'] == 'pull_request' and other_node['type'] == 'pull_request':
		duo_pr_pr.append([node, other_node])
	elif node['type'] == 'pull_request' and other_node['type'] == 'issue':
		duo_pr_issue.append([node, other_node])

pattern_json['duo_issue_issue'] = duo_issue_issue
pattern_json['duo_issue_pr'] = duo_issue_pr
pattern_json['duo_pr_pr'] = duo_pr_pr
pattern_json['duo_pr_issue'] = duo_pr_issue

print(pattern_json)