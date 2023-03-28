with [43529, 92173, 56349, 56350, 56355, 53854, 53855, 53860, 53861, 61030, 57447, 61029, 61035, 68741, 68742, 90257, 68768, 15019, 6833, 3252, 3253, 57529, 6842, 57530, 90300, 90299, 81091, 33989, 33990, 33991, 57552, 87767, 87768, 87784, 6892, 6893, 34030, 34031, 69361, 69362, 69363, 69366, 54016, 54017, 54018, 34058, 3347, 6950, 90932, 90933, 90953, 81229, 81230, 86349, 81234, 43353, 36698, 36699, 43354, 86361, 36703, 60257, 60258, 60259, 69990, 69991, 70008, 39816, 39817, 39818, 83356, 83357, 83358, 28581, 28583, 80808, 80814, 86446, 29104, 29105, 29106, 15802, 15806, 87487, 87496, 87497, 29132, 40420, 40421, 40422, 9199, 92150, 92151, 80890, 57342, 57343] as known_stacks // see cypher_scripts/fetch_all_pr_stack_ids
match (pr:pull_request)-[r1]->(pr_2:pull_request)-[r2]->(pr_3:pull_request)
where pr.creation_date < pr_2.creation_date < pr_3.creation_date
optional match (optional_issue:issue)-[optional_r]-(pr)
unwind [pr.number, pr_2.number, pr_3.number] as number_list
unwind [pr.status, pr_2.status, pr_3.status] as status_list
unwind [pr.user, pr_2.user, pr_3.user] as user_list
with pr, pr_2, pr_3, collect(distinct number_list) as number_list, [r1,r2] as match_relationships, optional_issue, optional_r, status_list,user_list, count(user_list) as user_counts, known_stacks
where optional_issue = null or (not (optional_issue)--(pr_2) and not (optional_issue)--(pr_3))
with pr, pr_2, pr_3, number_list, match_relationships, status_list, optional_issue, optional_r, apoc.agg.maxItems(user_list, user_counts) as max_users, known_stacks
where size(number_list) = 3 and not (:pull_request)-->(pr) and not (pr_3)-->(:pull_request) and size([i in status_list where i = "merged"]) >= 3/2 and max_users.value >= 3/2
call apoc.path.subgraphAll(pr, {limit: 50, bfs:true})
yield nodes, relationships
with pr, pr_2, pr_3, [id(pr), id(pr_2), id(pr_3)] as all_ids, optional_issue, optional_r, size(collect([i_node in nodes where i_node.type="pull_request" and i_node.number <> pr.number and not id(i_node) in known_stacks])) as not_stack, size(nodes) as len_nodes, nodes, relationships, match_relationships
return pr, pr_2, pr_3, all_ids, optional_issue, optional_r, nodes, relationships, toFloat(not_stack) / toFloat(len_nodes) as proportion, match_relationships
