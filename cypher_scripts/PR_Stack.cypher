//PR Stack
//match (pr:pull_request)-->(pr_2:pull_request)-->(pr_3:pull_request)-->(pr_4:pull_request)-->(pr_5:pull_request)-->(pr_6:pull_request)-->(pr_7:pull_request)-->(pr_8:pull_request)-->(pr_9:pull_request)-->(pr_10:pull_request)-->(pr_11:pull_request)-->(pr_12:pull_request)-->(pr_13:pull_request)-->(pr_14:pull_request)-->(pr_15:pull_request)
//unwind [pr.number, pr_2.number, pr_3.number, pr_4.number, pr_5.number, pr_6.number,pr_7.number,pr_8.number,pr_9.number,pr_10.number, pr_11.number,pr_12.number,pr_13.number, pr_14.number, pr_15.number] as number_list
//with pr, pr_2, pr_3, pr_4, pr_5,pr_6, pr_7, pr_8,pr_9,pr_10,pr_11,pr_12,pr_13,pr_14,pr_15, collect(distinct number_list) as number_list
//where size(number_list) = 15 and pr.creation_date < pr_2.creation_date < pr_3.creation_date < pr_4.creation_date< pr_5.creation_date < pr_6.creation_date < pr_7.creation_date < pr_8.creation_date < pr_9.creation_date < pr_10.creation_date<pr_11.creation_date < pr_12.creation_date < pr_13.creation_date < pr_14.creation_date < pr_15.creation_date and pr.user = pr_2.user = pr_3.user = pr_4.user = pr_5.user = pr_6.user = pr_7.user = pr_8.user = pr_9.user = pr_10.user = pr_11.user = pr_12.user=pr_13.user = pr_14.user = pr_15.user and pr.status = "merged" and pr_2.status = "merged" and pr_3.status = "merged" and pr_4.status = "merged" and pr_5.status = "merged" and pr_6.status = "merged" and pr_7.status = "merged" and pr_8.status = "merged" and pr_9.status = "merged" and pr_10.status = "merged" and pr_11.status = "merged" and pr_12.status = "merged" and pr_13.status = "merged" and pr_14.status = "merged" and pr_15.status = "merged" and not (:pull_request)-->(pr) and not (pr_15)-->(:pull_request)
//call apoc.path.subgraphAll(pr, {limit: 50, bfs: true })
//yield nodes, relationships
////return pr, pr_2, pr_3, pr_4, pr_5, pr_6, pr_7, nodes, relationships
//return pr, nodes, relationships
//match (pr:pull_request)-->(pr_2:pull_request)-->(pr_3:pull_request)-->(pr_4:pull_request)
//unwind [pr.number, pr_2.number, pr_3.number,pr_4.number] as number_list
//with pr, pr_2, pr_3, pr_4,collect(distinct number_list) as number_list
//where size(number_list) = 4 and pr.creation_date < pr_2.creation_date < pr_3.creation_date <pr_4.creation_date and not (:pull_request)-->(pr) and not (pr_4)-->(:pull_request)
//call apoc.path.subgraphAll(pr, {limit: 50, bfs: true })
//yield nodes, relationships
//return pr, pr_2, pr_3, pr_4, nodes, relationships
match (pr:pull_request)-->(pr_2:pull_request)-->(pr_3:pull_request)
unwind [pr.number, pr_2.number, pr_3.number] as number_list
with pr, pr_2, pr_3, collect(distinct number_list) as number_list
where size(number_list) = 3 and pr.creation_date < pr_2.creation_date < pr_3.creation_date and pr.user = pr_2.user = pr_3.user and not (:pull_request)-->(pr) and not (pr_3)-->(:pull_request)
call apoc.path.subgraphAll(pr, {limit: 50, bfs: true })
yield nodes, relationships
return pr, pr_2, pr_3, nodes, relationships
