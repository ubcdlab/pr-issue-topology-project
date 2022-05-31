import json 

f = open('graph.txt')
data = json.load(f)

def find_sinks(data):
	# a sink is a node with no outgoing edges.
	# whether the node has incoming edges or not is irrelevant.
	# therefore, an isolated node (degree 0) or not are both sinks.
	sinks = []
	for index in data.keys():
		item = data.get(str(index))
		if len(item) == 0: 
			sinks.append(index)
	return sinks

def find_isolated_nodes(data):
	# an isolated node is a node with no incoming or outgoing edges.
	isolated = list(data.keys())
	for destination in data.values():
		for entry in destination:
			if entry in isolated:
				isolated.remove(entry)
	for node in isolated:
		item = data.get(node)
		if len(item) > 0:
			isolated.remove(node) 
	return isolated

def find_source_nodes(data):
	# a source is a node with no incoming edges.
	source = list(data.keys())
	for destination in data.values():
		for entry in destination:
			if entry in source:
				source.remove(entry)
	return source

def find_loops(data):
	loops = []
	for node in data.keys():
		outgoing = data.get(node)
		if node in outgoing:
			loops.append(node)
	return loops


# statistics
total_sinks = find_sinks(data)
total_isolated = find_isolated_nodes(data)
total_source = find_source_nodes(data)
total_loop = find_loops(data)
nodes = len(data.keys())


print(f"Total number of nodes: {nodes}")
print(f"Source nodes: {len(total_source)} ({round(len(total_source)/nodes * 100, 2)}%)")
print(f"Sink nodes: {len(total_sinks)} ({round(len(total_sinks)/nodes * 100, 2)}%)")
print(f"Isolated nodes: {len(total_isolated)} ({round(len(total_isolated)/nodes * 100, 2)}%)")
print(f"Loop nodes: {len(total_loop)} ({round(len(total_loop)/nodes * 100, 2)}%)")

counter = 0
for destination in data.values():
	for entry in destination:
		counter += 1
print(f"Total outgoing edges: {counter}")

# print(sinks)
# print(isolated)


