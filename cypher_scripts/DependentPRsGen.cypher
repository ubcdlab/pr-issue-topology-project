match (pr:pull_request)-[r1]->(pr_2:pull_request)-[r2]->(pr_3:pull_request)-[r3]->(pr_4:pull_request)
where pr.creation_date < pr_2.creation_date < pr_3.creation_date < pr_4.creation_date
optional match (optional_issue:issue)-[optional_r]-(pr)
unwind [pr.number, pr_2.number, pr_3.number, pr_4.number] as number_list
unwind [pr.status, pr_2.status, pr_3.status, pr_4.status] as status_list
unwind [pr.user, pr_2.user, pr_3.user, pr_4.user] as user_list
with pr, pr_2, pr_3, pr_4, collect(distinct number_list) as number_list, [r1, r2, r3] as match_relationships, status_list, optional_issue, optional_r, user_list, count(user_list) as user_counts
where optional_issue = null or (not (optional_issue)--(pr_2) and not (optional_issue)--(pr_3) and not (optional_issue)--(pr_4))
with pr, pr_2, pr_3, pr_4, number_list, match_relationships, status_list, optional_issue, optional_r, apoc.agg.maxItems(user_list, user_counts) as max_users
where size(number_list) = 4 and not (:pull_request)-->(pr) and not (pr_4)-->(:pull_request) and size([i in status_list where i = "merged"]) >= 4/2 and max_users.value >= 4/2
call apoc.path.subgraphAll(pr, {limit: 50, bfs: true})
yield nodes, relationships
return pr, nodes, relationships, match_relationships, pr_2, pr_3, pr_4, [id(pr), id(pr_2), id(pr_3), id(pr_4)] as all_ids, optional_issue, optional_r