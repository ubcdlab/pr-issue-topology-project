//Complex / Large
profile match (n {status: "closed"})
call apoc.path.subgraphAll(n, {limit: 500})
yield nodes, relationships
where size(nodes) >= 20 and size([n in nodes where n.status="closed"]) >= size(nodes) / 2 and size([n in nodes where n.type="pull_request" and n.status="merged"]) = 1
return nodes, relationships