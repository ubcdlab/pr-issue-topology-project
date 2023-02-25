// Same Author
match (i:issue {status: "closed"})-[{labels: "fixes"}]-(p:pull_request {status: "merged"})
where i.user = p.user
call apoc.path.subgraphAll(i, {limit: 50, bfs:true})
yield nodes, relationships
return i, p, nodes, relationships
