//Optimization
match (pr:pull_request)-[r {labels:"fixes"}]->(i:issue)
where pr.status = "merged"
with pr, collect(i) as issues
where size([issue in issues where issue.status="closed"]) > 1 and size(issues) > 1
with pr, [issue in issues where issue.status="closed"] as closed_issues
return pr,closed_issues