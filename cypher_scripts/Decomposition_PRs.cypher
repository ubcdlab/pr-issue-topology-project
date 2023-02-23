//Decomposition w PRs
call {match (i:issue {status: "closed"})-[r {labels: "fixes"}]-(pr:pull_request {status: "merged"})
with i, collect(distinct pr) as pull_requests
where size(pull_requests) > 1
return i,pull_requests
union
match (hub_pr:pull_request {status:"merged"})--(spoke_pr:pull_request {status:"merged"})
with hub_pr, collect(distinct spoke_pr) as spokes
where size(spokes) > 1
with hub_pr as i, spokes as pull_requests
return i, pull_requests
}
call apoc.path.subgraphAll(i, {limit: case 50 > size(pull_requests) when true then 50 when false then size(pull_requests) + 1 end, bfs: true })
yield nodes, relationships
return i, pull_requests, nodes, relationships
