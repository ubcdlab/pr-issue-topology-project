import json 

f = open('graph.txt')
data = json.load(f)

vis_data = {
	"nodes": [],
	"links": []
}

for key, value in data.items():
	# key is node number
	

	# create a node entry
	node = {"id": int(key), "name": str(key), "type": value['type'], "status": value['status']}
	vis_data['nodes'].append(node)
	for destination in value['links']: # create the links entry
		linking = {"source": int(key), "target": int(destination)}
		vis_data['links'].append(linking)

print(f"total links: {len(vis_data['links'])}")

with open('data/vis_graph.json', 'w') as f:
	f.write(json.dumps(vis_data, indent=4))