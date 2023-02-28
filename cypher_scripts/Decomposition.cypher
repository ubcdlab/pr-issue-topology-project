//Decomposition w/ Subgraphs
match (i:issue {status: "closed"})-[r {labels: "fixes"}]-(pr:pull_request {status: "merged"})
with i, collect(distinct pr) as pull_requests, collect(distinct r) as match_relationships
where size(pull_requests) > 1
call apoc.path.subgraphAll(i, {limit: case 50 > size(pull_requests) when true then 50 when false then size(pull_requests) + 1 end, bfs: true })
yield nodes, relationships
return i, pull_requests, nodes, relationships, match_relationships
