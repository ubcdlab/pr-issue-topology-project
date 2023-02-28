//Duplicate HubWProportions
match (i:issue)-[r {labels:"duplicate"}]-(i2:issue)
where i2.creation_date > i.creation_date
with i, collect(distinct i2) as spoke_issues
where size(spoke_issues) > 1
call apoc.path.subgraphAll(i, {limit: case when 50 > size(spoke_issues) then 50 else size(spoke_issues) + 1 end, bfs:true})
yield nodes, relationships
with i, nodes, [7654, 10439, 8818, 9497, 9427, 12837, 12886, 24044, 34495, 36134, 40437, 41058, 52611, 52613, 52698, 53345, 53132, 53355, 53407, 56580, 55655, 61605, 61996, 68405, 77663, 76315, 75603, 75962, 75845, 75965, 76357, 77364, 77402, 78584, 78648, 77484, 77119, 77317, 78228, 78685, 78657, 80083, 81090, 84603, 88889, 89587] as known_dups
with i, size(collect([i_node in nodes where i_node.type="issue" and i_node.number <> i.number and not id(i_node) in known_dups])) as not_dups, size(nodes) as len_nodes
return i, toFloat(not_dups) / toFloat(len_nodes) as proportion
