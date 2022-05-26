import json 

f = open('graph.txt')
data = json.load(f)

# statistics
sinks = []
isolated = []
nodes = len(data.keys())
maximum_key = list(data.keys())[-1]

for index in range(1, int(maximum_key)):
	item = data.get(str(index), None)
	if item is None:
		continue
	if len(item) == 0:
		sinks.append(index)

for index in data.keys():
	is_isolated = True
	item = data.get(index)
	if len(item) > 0:
		continue
	for entry in data.values():
		if index in entry:
			is_isolated = False
	if (is_isolated):
		isolated.append(index)

print(f"Total number of nodes: {nodes}")
print(f"Sink nodes: {len(sinks)} ({round(len(sinks)/nodes * 100, 2)}%)")
print(f"Isolated nodes: {len(isolated)} ({round(len(isolated)/nodes * 100, 2)}%)")

print(sinks)
print(isolated)