//Improvement
match (pr1:pull_request)-[r {labels:"fixes"}]->(i:issue),(pr1)--(pr2:pull_request),(pr2)-->(i)
where i.status ="closed" and pr1.status="merged" and pr2.status="merged" and pr2.creation_date > pr1.creation_date
call apoc.path.subgraphAll(i, {limit: 50})
yield nodes, relationships
return i, pr1, pr2, nodes, relationships
