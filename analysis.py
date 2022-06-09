import json 

f = open('data/graph.json')
# f = open('data/vis_graph.json')
data = json.load(f)
pattern_json = {}

print(len(data['nodes']))
isolated = []
for component in data['connected_components']:
	if len(component) == 1:
		isolated.append(component)
print(len(isolated))
pattern_json['isolated'] = isolated

print(pattern_json)