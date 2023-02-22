match (i:issue)<-[r {labels:"fixes"}]-(pr:pull_request)
where i.status = "closed"
with i, collect(pr) as pull_requests
where size([p_r in pull_requests where p_r.status="merged"]) = 1 and size([p_r in pull_requests where p_r.status="closed"]) >= 1 and size(pull_requests) >= 2
with i as central, pull_requests as prs_1
match (central)<-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (i2:issue)--(p)
where i2.creation_date > p.creation_date
with central, prs_1, p as p_2, i2 as i2_2
call apoc.path.subgraphAll(central, {limit: 50})
yield nodes, relationships
return central, p_2, i2_2, prs_1, nodes,relationships
