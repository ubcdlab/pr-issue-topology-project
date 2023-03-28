call {
match (pr:pull_request {status: "merged"})-[r {labels:"fixes"}]-(i:issue)
with pr, collect(distinct i) as issues, collect(distinct r) as match_relationships
where size([issue in issues where issue.status="closed"]) > 1
return collect(distinct id(pr)) as known_optimization
}

match (pr:pull_request {status: "merged"})-[r {labels:"fixes"}]-(i:issue)
with pr, collect(distinct i) as issues, collect(distinct r) as match_relationships, known_optimization
where size([issue in issues where issue.status="closed"]) > 1
with pr, [issue in issues where issue.status="closed"] as closed_issues, match_relationships, known_optimization
call apoc.path.subgraphAll(pr, {limit: case 50 > size(closed_issues) + 1 when true then 50 when false then size(closed_issues) + 1 end, bfs: true })
yield nodes, relationships
with pr, closed_issues, nodes, relationships, match_relationships, size(collect([i_node in nodes where i_node.type="pull_request" and i_node.status="merged" and i_node.number <> pr.number and not id(i_node) in known_optimization])) as not_op, size(nodes) as len_nodes
return pr, closed_issues, nodes, relationships, match_relationships, toFloat(not_op) / toFloat(len_nodes) as proportion
