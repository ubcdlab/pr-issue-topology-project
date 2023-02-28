// Consequence-1
match (i:issue {status:"closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (i2:issue)-[r2]-(p)
where i2.creation_date > p.creation_date and i.number <> i2.number
call apoc.path.subgraphAll(i, {limit: 50, bfs: true })
yield nodes, relationships
with i, p, i2, nodes, relationships, collect(distinct r)+collect(distinct r2) as match_relationships
return i, p, i2, nodes, relationships, match_relationships
