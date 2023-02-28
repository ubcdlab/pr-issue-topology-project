//Optimization
match (pr:pull_request)-[r {labels:"fixes"}]-(i:issue)
where pr.status = "merged"
with pr, collect(distinct i) as issues, collect(distinct r) as match_relationships
where size([issue in issues where issue.status="closed"]) > 1
with pr, [issue in issues where issue.status="closed"] as closed_issues, match_relationships
call apoc.path.subgraphAll(pr, {limit: case 50 > size(closed_issues) + 1 when true then 50 when false then size(closed_issues) + 1 end, bfs: true })
yield nodes, relationships
return pr, closed_issues, nodes, relationships, match_relationships
