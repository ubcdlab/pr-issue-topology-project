// Consequence-3
match (i:issue {status:"closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (p)-[r2]-(:issue)-[r3]-(p2:pull_request)
where p2.number <> p.number and p2.creation_date > p.creation_date and p.user <> p2.user
with i, p,p2, [r,r2,r3] as match_relationships, collect(distinct id(i)) as known_consq
call apoc.path.subgraphAll(i, {limit: 50, bfs: true })
yield nodes, relationships
with i, p, p2, nodes, relationships, match_relationships, size(collect([i_node in nodes where i_node.type="issue" and i_node.status="closed" and i_node.number <> i.number and not id(i_node) in known_consq])) as not_consq, size(nodes) as len_nodes
return i, p, p2, nodes, relationships, match_relationships, toFloat(not_consq) / toFloat(len_nodes) as proportion

union 

match (i:issue {status:"closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (p)-[r2]-(p2:pull_request)
where p2.number <> p.number and p2.creation_date > p.creation_date and p.user <> p2.user
with i, p,p2, [r,r2] as match_relationships, collect(distinct id(i)) as known_consq
call apoc.path.subgraphAll(i, {limit: 50, bfs: true })
yield nodes, relationships
with i, p, p2, nodes, relationships, match_relationships, size(collect([i_node in nodes where i_node.type="issue" and i_node.status="closed" and i_node.number <> i.number and not id(i_node) in known_consq])) as not_consq, size(nodes) as len_nodes
return i, p, p2, nodes, relationships, match_relationships, toFloat(not_consq) / toFloat(len_nodes) as proportion
