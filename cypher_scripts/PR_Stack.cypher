// PR Stack
match (pr:pull_request)-[r1]->(pr_2:pull_request)-[r2]->(pr_3:pull_request)
where pr.creation_date < pr_2.creation_date < pr_3.creation_date
optional match (optional_issue:issue)-[optional_r]-(pr)
unwind [pr.number, pr_2.number, pr_3.number] as number_list
unwind [pr.status, pr_2.status, pr_3.status] as status_list
unwind [pr.user, pr_2.user, pr_3.user] as user_list
with pr, pr_2, pr_3, collect(distinct number_list) as number_list, [r1,r2] as match_relationships, collect(distinct id(pr))+collect(distinct id(pr_2))+collect(distinct id(pr_3)) as known_stacks, optional_issue, optional_r, status_list,user_list, count(user_list) as user_counts
where optional_issue = null or (not (optional_issue)--(pr_2) and not (optional_issue)--(pr_3))
with pr, pr_2, pr_3, number_list, match_relationships, status_list, optional_issue, optional_r, apoc.agg.maxItems(user_list, user_counts) as max_users, known_stacks
where size(number_list) = 3 and not (:pull_request)-->(pr) and not (pr_3)-->(:pull_request) and size([i in status_list where i = "merged"]) >= 3/2 and max_users.value >= 3/2
call apoc.path.subgraphAll(pr, {limit: 50, bfs:true})
yield nodes, relationships
with pr, pr_2, pr_3, [id(pr), id(pr_2), id(pr_3)] as all_ids, optional_issue, optional_r, size(collect([i_node in nodes where i_node.type="pull_request" and i_node.number <> pr.number and not id(i_node) in known_stacks])) as not_stack, size(nodes) as len_nodes, nodes, relationships, match_relationships
return pr, pr_2, pr_3, all_ids, optional_issue, optional_r, nodes, relationships, toFloat(not_stack) / toFloat(len_nodes) as proportion, match_relationships
