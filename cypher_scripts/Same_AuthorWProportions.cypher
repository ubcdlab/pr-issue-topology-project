// Same AuthorWProportions
match (i:issue {status: "closed"})-[{labels: "fixes"}]-(p:pull_request {status: "merged"})
where i.user = p.user
with i, collect(distinct id(i)) as known_sa
call apoc.path.subgraphAll(i, {limit: 50,bfs:true})
yield nodes, relationships
with i, size(collect([i_node in nodes where i_node.type="issue" and i_node.status="closed" and i_node.number <> i.number and not id(i_node) in known_sa])) as not_comp, size(nodes) as len_nodes, nodes
return i, toFloat(not_comp) / toFloat(len_nodes) as proportion, nodes
