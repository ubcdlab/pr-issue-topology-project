// Release
match (i:issue {status:"closed"})-[r]-(pr:pull_request{status:"merged"})
where i.creation_date > pr.creation_date
with i, collect(distinct pr) as prs, collect(r) as match_relationships, collect(distinct id(i)) as known_releases
where size(prs) >= 2
call apoc.path.subgraphAll(i, {limit: case 50 > size(prs) when true then 50 when false then size(prs) + 1 end, bfs: true })
yield nodes, relationships
with i, prs, match_relationships, nodes, relationships, size(collect([i_node in nodes where i_node.type="issue" and i_node.status="closed" and i_node.number <> i.number and not id(i_node) in known_releases])) as not_release, size(nodes) as len_nodes
return i, prs, match_relationships, nodes, relationships, toFloat(not_release) / toFloat(len_nodes) as proportion
