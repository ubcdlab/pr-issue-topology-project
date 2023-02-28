// Consequence-2
match (i:issue {status:"closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (i2:issue {status:"closed"})--(p), (i2)<--(p2:pull_request {status:"merged"})
where (i2.creation_date > p.creation_date or i2.creation_date > i.creation_date) and i.number <> i2.number and p.number <> p2.number
call apoc.path.subgraphAll(i, {limit: 50, bfs: true })
yield nodes, relationships
with i, p, i2, p2, nodes, relationships, collect(distinct r) as match_relationships
return i, p, i2, p2, nodes, relationships, match_relationships
