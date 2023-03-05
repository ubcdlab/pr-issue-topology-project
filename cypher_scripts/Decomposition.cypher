//Decomposition w/ Subgraphs
match (i:issue {status: "closed"})-[r {labels: "fixes"}]-(pr:pull_request), (i)-[r2 {labels: "fixes"}]-(pr_2:pull_request)
where not (pr)--(pr_2) and pr.number <> pr_2.number and (pr.status = "closed" and (pr)--(pr_2) and pr_2.status="merged" or pr.status <> "closed")
with i, collect(distinct pr)+collect(distinct pr_2) as pull_requests, collect(distinct r)+collect(distinct r2) as match_relationships
where size(pull_requests) > 1 and size([p in pull_requests where p.status = "merged"]) >= toFloat(size(pull_requests))/ toFloat(2)
call apoc.path.subgraphAll(i, {limit: case 50 > size(pull_requests) when true then 50 when false then size(pull_requests) + 1 end, bfs: true })
yield nodes, relationships
return i, pull_requests, nodes, relationships, match_relationships
