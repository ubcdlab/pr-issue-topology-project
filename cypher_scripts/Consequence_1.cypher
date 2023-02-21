// Consequence-1
match (i:issue {status:"closed"})<-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (i2:issue)--(p)
where i2.creation_date > p.creation_date and i.number <> i2.number 
call apoc.path.subgraphAll(i, {limit: 50})
yield nodes, relationships
return i, p, i2, nodes, relationships
