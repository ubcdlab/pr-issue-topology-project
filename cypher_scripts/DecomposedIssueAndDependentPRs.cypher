match (i_1:issue {status: "closed"})-[r {labels: "fixes"}]-(pr_1:pull_request), (i)-[r2 {labels: "fixes"}]-(pr2_1:pull_request)
where not (pr_1)--(pr2_1) and pr_1.number <> pr2_1.number and (pr_1.status = "closed" and (pr_1)--(pr2_1) and pr2_1.status="merged" or pr_1.status <> "closed")
with i_1, collect(distinct pr_1)+collect(distinct pr2_1) as pull_requests_1, collect(distinct r)+collect(distinct r2) as match_relationships_1, [i_1]+collect(pr_1)+collect(pr2_1) as decomposition_match
where size(pull_requests_1) > 1 and size([p in pull_requests_1 where p.status = "merged"]) >= toFloat(size(pull_requests_1))/ toFloat(2)

match (pr_2:pull_request)-[r1]->(pr2_2:pull_request)-[r2]->(pr3_2:pull_request)
where pr_2.creation_date < pr2_2.creation_date < pr3_2.creation_date
optional match (optional_issue_2:issue)-[optional_r_2]-(pr_2)
unwind [pr_2.number, pr2_2.number, pr3_2.number] as number_list
unwind [pr_2.status, pr2_2.status, pr3_2.status] as status_list
unwind [pr_2.user, pr2_2.user, pr3_2.user] as user_list
with i_1, pull_requests_1, match_relationships_1, pr_2, pr2_2, pr3_2, collect(distinct number_list) as number_list, [r1,r2] as match_relationships_2, optional_issue_2, optional_r_2, status_list,user_list, count(user_list) as user_counts, decomposition_match
where optional_issue_2 = null or (not (optional_issue_2)--(pr2_2) and not (optional_issue_2)--(pr3_2))
with i_1, pull_requests_1, match_relationships_1, pr_2, pr2_2, pr3_2, number_list, match_relationships_2, status_list, optional_issue_2, optional_r_2, apoc.agg.maxItems(user_list, user_counts) as max_users , decomposition_match
where size(number_list) = 3 and not (:pull_request)-->(pr_2) and not (pr3_2)-->(:pull_request) and size([i in status_list where i = "merged"]) >= 3/2 and max_users.value >= 3/2 and (pr_2 in decomposition_match or pr2_2 in decomposition_match or pr3_2 in decomposition_match)
with i_1, pull_requests_1, match_relationships_1, pr_2, pr2_2, pr3_2, match_relationships_2, optional_issue_2, optional_r_2, apoc.coll.intersection(decomposition_match, [pr_2,pr2_2,pr3_2]) as intersection

call apoc.path.subgraphAll(intersection[0], {limit: case 50 > size(pull_requests_1) + 4 when true then 50 when false then size(pull_requests_1) + 4 end, bfs: true })
yield nodes, relationships
return i_1, pull_requests_1, match_relationships_1, pr_2, pr2_2, pr3_2, match_relationships_2, optional_issue_2, optional_r_2, nodes, relationships, intersection as central

limit 10
