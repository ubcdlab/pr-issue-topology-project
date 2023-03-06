// Same Author
match (i:issue {status: "closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"})
where i.user = p.user
with i, p, r, collect(distinct id(i)) as known_sa
call apoc.path.subgraphAll(i, {limit: 50, bfs:true})
yield nodes, relationships
with i,p, r, nodes, relationships, size(collect([i_node in nodes where i_node.type="issue" and i_node.status="closed" and i_node.number <> i.number and not id(i_node) in known_sa])) as not_sa, size(nodes) as len_nodes
return i, p, nodes, relationships, [r] as match_relationships, toFloat(not_sa) / toFloat(len_nodes) as proportion
