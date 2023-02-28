// Same Author
match (i:issue {status: "closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"})
where i.user = p.user
call apoc.path.subgraphAll(i, {limit: 50, bfs:true})
yield nodes, relationships
with i, p, nodes, relationships, collect(distinct r) as match_relationships
return i, p, nodes, relationships, match_relationships
