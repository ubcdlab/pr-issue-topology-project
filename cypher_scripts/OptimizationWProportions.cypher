//OptimizationWProportions
match (pr:pull_request)-[r {labels:"fixes"}]->(i:issue)
where pr.status = "merged"
with pr, collect(distinct i) as issues
where size([issue in issues where issue.status="closed"]) > 1 and size(issues) > 1
with pr, [issue in issues where issue.status="closed"] as closed_issues
with pr, closed_issues, [115, 161, 211, 1017, 1095, 2078, 2101, 3119, 3687, 4144, 4295, 4301, 4607, 4681, 4948, 8282, 9144, 9198, 9782, 10097, 10833, 13864, 16223, 19465, 19963, 20093, 20311, 20430, 20694, 20853, 20987, 21278, 21614, 22514, 22521, 22635, 22662, 23569, 23597, 24283, 27210, 29227, 29681, 30048, 31902, 33628, 34834, 36833, 36837, 36847, 39704, 39705, 39731, 39971, 45049, 46071, 53535, 54608, 54637, 55241, 61672, 61675, 61722, 61787, 61807, 61832, 61910, 62009, 62022, 62094, 62139, 62149, 62271, 63485, 63718, 63764, 63880, 64366, 64473, 64746, 64840, 64853, 64860, 64864, 66190, 66697, 68447, 68910, 69722, 70015, 75237, 75888, 79694, 79863, 79909, 79911, 79919, 79985, 80058, 80103, 80154, 80297, 80412, 80538, 81558, 83249, 83483, 83491, 83494, 85335, 85539, 85782, 87500, 88722, 89372, 90667, 91937, 92135] as known_optimization
call apoc.path.subgraphAll(pr, {limit: case 50 > size(closed_issues) + 1 when true then 50 when false then size(closed_issues) + 1 end, bfs: true })
yield nodes,relationships
with pr, size(collect([i_node in nodes where i_node.type="pull_request" and i_node.status="merged" and i_node.number <> pr.number and not id(i_node) in known_optimization])) as not_op, size(nodes) as len_nodes, nodes
return pr, toFloat(not_op) / toFloat(len_nodes) as proportion, nodes
