// Consequence-1
call {
match (i:issue {status:"closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (i2:issue)-[r2]-(p)
where i2.creation_date > p.creation_date and i.number <> i2.number
return collect(distinct id(i)) as known_consq
}

match (i:issue {status:"closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (i2:issue)-[r2]-(p)
where i2.creation_date > p.creation_date and i.number <> i2.number
with i, p, i2, [r,r2] as match_relationships, known_consq
call apoc.path.subgraphAll(i, {limit: 50, bfs: true })
yield nodes, relationships
with i, p, i2, nodes, relationships, match_relationships,  size(collect([i_node in nodes where i_node.type="issue" and i_node.status="closed" and i_node.number <> i.number and not id(i_node) in known_consq])) as not_consq, size(nodes) as len_nodes
return i, p, i2, nodes, relationships, match_relationships,toFloat(not_consq) / toFloat(len_nodes) as proportion
