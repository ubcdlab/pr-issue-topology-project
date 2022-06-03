import json

'''
Today on mathematics gear

I spend 1 hour independently rediscovering 2nd year CS lecture materials
Hammond finds a python library that abstracts the above
and James imports the library
'''
import networkx as nx
graph = nx.Graph()

f = open('data/graph.json')
data = json.load(f)

for node in data['nodes']:
	graph.add_node(node['id'])
for link in data['links']:
	graph.add_edge(link['source'], link['target'])

connected_components = list(nx.connected_components(graph))
for component in connected_components:
	for node in component:
		for entry in data['nodes']:
			if (entry['id'] == node):
				entry['connected_component'] = component
print(data['nodes'])

# with open('data/vis_graph.json', 'w') as f:
# 	f.write(json.dumps(data, indent=4))