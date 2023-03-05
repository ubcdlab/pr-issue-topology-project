//PR Hub
call {match (pr:pull_request)-[r]->(pr_2:pull_request)-[r2]->(pr_3:pull_request)
unwind [pr.number, pr_2.number, pr_3.number] as number_list
unwind [pr.status, pr_2.status, pr_3.status] as status_list
with pr, pr_2, pr_3, collect(distinct number_list) as number_list, [r,r2] as match_relationships, [i in collect(status_list) where i <> "merged"] as non_merged
where size(number_list) = 3 and pr.creation_date < pr_2.creation_date < pr_3.creation_date and ((size(non_merged) <= 1 and (pr_3)-->(:pull_request)) or size(non_merged) = 0)
return collect(id(pr))+collect(id(pr_2))+collect(id(pr_3)) as all_ids
}
match (pr:pull_request)-[r]-(pr2:pull_request)
where pr2.creation_date < pr.creation_date and not id(pr) in all_ids and not id(pr2) in all_ids
with pr, collect(distinct pr2) as prs, collect(distinct pr2.user) as users, collect(distinct r) as match_relationships
where size(prs) >= 3 and size(users) >= 2
call apoc.path.subgraphAll(pr, {limit: case 50 > size(prs) when true then 50 when false then size(prs) + 1 end, bfs: true })
yield nodes, relationships
return pr, prs, nodes, relationships, match_relationships
