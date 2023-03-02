// Same Author
match (i:issue {status: "closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"})
where i.user = p.user
call apoc.path.subgraphAll(i, {limit: 50, bfs:true})
yield nodes, relationships
return i, p, nodes, relationships, [r] as match_relationships
