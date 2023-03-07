//Competition
match (i:issue)-[r {labels:"fixes"}]-(pr:pull_request)
where i.status = "closed"
with i, collect(distinct pr) as pull_requests, collect (distinct pr.user) as users, collect(r) as match_relationships, collect(distinct id(i)) as known_competition, max(pr.creation_date) as max_date, min(pr.creation_date) as min_date
where size([p_r in pull_requests where p_r.status="merged"]) = 1 and size([p_r in pull_requests where p_r.status="closed"]) >= 1 and size(pull_requests) >= 2 and size(users) > 1 and max_date - min_date <= 604800 // dates are in Unix timestamps so difference is in seconds
call apoc.path.subgraphAll(i, {limit: case 50 > size(pull_requests) when true then 50 when false then size(pull_requests) + 1 end, bfs: true })
yield nodes, relationships
with i, pull_requests, match_relationships, nodes, relationships, size(collect([i_node in nodes where i_node.type="issue" and i_node.status="closed" and i_node.number <> i.number and not id(i_node) in known_competition])) as not_comp, size(nodes) as len_nodes
return i, pull_requests, match_relationships, nodes, relationships, toFloat(not_comp) / toFloat(len_nodes) as proportion
