//ImprovementWProportions
match (pr1:pull_request)-[r {labels:"fixes"}]->(i:issue),(pr1)--(pr2:pull_request),(pr2)--(i)
where i.status ="closed" and pr1.status="merged" and pr2.status="merged" and pr2.creation_date > pr1.creation_date
call apoc.path.subgraphAll(i, {limit: 50, bfs:true})
yield nodes, relationships
with i, nodes, [429, 2084, 8997, 9269, 9357, 12144, 19822, 19883, 20194, 20752, 21416, 22844, 23666, 24192, 25827, 25996, 26475, 27214, 27324, 31151, 35229, 33036, 33497, 39416, 39638, 39648, 39677, 39668, 51858, 61707, 61818, 62122, 63347, 62765, 64223, 64464, 64657, 64604, 66140, 78935, 79696, 79809, 80037, 79841, 79884, 79962, 79970, 80453, 80165, 80493, 80616, 81345, 86701, 89477] as known_improvement
with i, size(collect([i_node in nodes where i_node.type="issue" and i_node.status="closed" and i_node.number <> i.number and not id(i_node) in known_improvement])) as not_imp, size(nodes) as len_nodes
return i, toFloat(not_imp) / toFloat(len_nodes) as proportion
