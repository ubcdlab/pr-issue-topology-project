//Decomposition w/ Subgraphs
match (i:issue {status: "closed"})<-[r {labels: "fixes"}]-(pr:pull_request {status: "merged"})
with i, collect(pr) as pull_requests
where size(pull_requests) > 1
call apoc.path.subgraphAll(i, {limit: 50})
yield nodes, relationships
return i, pull_requests, nodes, relationships
