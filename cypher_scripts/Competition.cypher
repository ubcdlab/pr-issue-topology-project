//Competition
match (i:issue)-[r {labels:"fixes"}]-(pr:pull_request)
where i.status = "closed"
with i, collect(distinct pr) as pull_requests, collect (distinct pr.user) as users, collect(distinct r) as match_relationships
where size([p_r in pull_requests where p_r.status="merged"]) = 1 and size([p_r in pull_requests where p_r.status="closed"]) >= 1 and size(pull_requests) >= 2 and size(users) > 1
call apoc.path.subgraphAll(i, {limit: case 50 > size(pull_requests) when true then 50 when false then size(pull_requests) + 1 end, bfs: true })
yield nodes, relationships
return i, pull_requests, match_relationships, nodes, relationships
