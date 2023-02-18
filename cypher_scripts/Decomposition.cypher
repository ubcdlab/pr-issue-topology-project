// Decomposition
match (i:issue {status: "closed"})<-[r {labels: "fixes"}]-(pr:pull_request {status: "merged"})
with i, collect(pr) as pull_requests
where size(pull_requests) > 1
return i, pull_requests