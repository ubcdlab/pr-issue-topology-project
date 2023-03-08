//Duplicate Hub
call {
match (i:issue)-[r {labels:"duplicate"}]-(i2:issue)
where i2.creation_date > i.creation_date and i2.user <> i.user
with i, collect(distinct i2) as spoke_issues, collect(distinct r) as match_relationships, collect(distinct id(i)) as known_dups
where size(spoke_issues) > 1
return apoc.coll.toSet(apoc.coll.flatten(collect(known_dups))) as known_dups
}

match (i:issue)-[r {labels:"duplicate"}]-(i2:issue)
where i2.creation_date > i.creation_date and i2.user <> i.user
with i, collect(distinct i2) as spoke_issues, collect(distinct r) as match_relationships, known_dups
where size(spoke_issues) > 1
call apoc.path.subgraphAll(i, {limit: case 50 > size(spoke_issues) when true then 50 when false then size(spoke_issues) + 1 end, bfs: true })
yield nodes, relationships
with i, spoke_issues, nodes, relationships, match_relationships, size(collect([i_node in nodes where i_node.type="issue" and i_node.number <> i.number and not id(i_node) in known_dups])) as not_dups, size(nodes) as len_nodes
return i, spoke_issues, nodes, relationships, match_relationships, toFloat(not_dups) / toFloat(len_nodes) as proportion
