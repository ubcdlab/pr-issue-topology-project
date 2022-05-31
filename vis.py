import json 

f = open('graph.txt')
data = json.load(f)

vis_data = {
	"nodes": [],
	"links": []
}

for key, value in data.items():
	node = {"id": int(key), "name": key}
	vis_data['nodes'].append(node)
	for destination in value:
		linking = {"source": int(key), "target": int(destination)}
		vis_data['links'].append(linking)

print(f"total links: {len(vis_data['links'])}")

with open('vis_graph.json', 'w') as f:
	f.write(json.dumps(vis_data, sort_keys=True, indent=4))