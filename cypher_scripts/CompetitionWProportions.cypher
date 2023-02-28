//CompetitionWProportions
match (i:issue)-[r {labels:"fixes"}]-(pr:pull_request)
where i.status = "closed"
with i, collect(distinct pr) as pull_requests, collect (distinct pr.user) as users
where size([p_r in pull_requests where p_r.status="merged"]) = 1 and size([p_r in pull_requests where p_r.status="closed"]) >= 1 and size(pull_requests) >= 2 and size(users) > 1
call apoc.path.subgraphAll(i, {limit: case 50 > size(pull_requests) when true then 50 when false then size(pull_requests) + 1 end, bfs: true })
yield nodes, relationships
with i, nodes, relationships, [784, 3198, 5647, 7457, 9022, 10733, 12007, 14778, 21258, 23590, 23658, 25946, 28089, 29844, 30861, 30952, 31266, 31504, 32213, 32766, 37063, 40437, 40521, 47094, 54617, 63548, 63667, 76896, 76908, 80172, 84112, 85528, 85549, 85662, 85848, 88727] as known_competition
with i, size(collect([i_node in nodes where i_node.type="issue" and i_node.status="closed" and i_node.number <> i.number and not id(i_node) in known_competition])) as not_comp, size(nodes) as len_nodes, nodes
return i, toFloat(not_comp) / toFloat(len_nodes) as proportion, nodes
