//Improvement
match (pr1:pull_request)-[r {labels:"fixes"}]-(i:issue),(pr1)-[r2]-(pr2:pull_request),(pr2)-[r3 {labels:"fixes"}]-(i)
where not id(pr1) in all_ids and not id(pr2) in all_ids and pr1.number<>pr2.number and i.status ="closed" and pr1.status="merged" and pr2.status="merged" and pr2.creation_date > pr1.creation_date
call apoc.path.subgraphAll(i, {limit: 50, bfs:true})
yield nodes, relationships
return i, pr1, pr2, nodes, relationships, [r,r2,r3] as match_relationships
