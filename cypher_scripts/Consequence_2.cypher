// Consequence-2
match (i:issue {status:"closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (i2:issue {status:"closed"})-[r2]-(p), (i2)-[r3]-(p2:pull_request {status:"merged"})
where (i2.creation_date > p.creation_date or i2.creation_date > i.creation_date) and i.number <> i2.number and p.number <> p2.number
with i, p, i2, p2, [r,r2,r3] as match_relationships, collect(distinct id(i)) as known_consq
call apoc.path.subgraphAll(i, {limit: 50, bfs: true })
yield nodes, relationships
with i, p, i2, p2, nodes, relationships, match_relationships, size(collect([i_node in nodes where i_node.type="issue" and i_node.status="closed" and i_node.number <> i.number and i_node.number <> i2.number and not id(i_node) in known_consq])) as not_consq, size(nodes) as len_nodes
return i, p, i2, p2, nodes, relationships, match_relationships, toFloat(not_consq) / toFloat(len_nodes) as proportion
