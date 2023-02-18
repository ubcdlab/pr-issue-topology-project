//Competition
match (i:issue)<-[r {labels:"fixes"}]-(pr:pull_request)
where i.status = "closed"
with i, collect(pr) as pull_requests
where size([p_r in pull_requests where p_r.status="merged"]) = 1 and size([p_r in pull_requests where p_r.status="closed"]) >= 1 and size(pull_requests) >= 2
return i, pull_requests