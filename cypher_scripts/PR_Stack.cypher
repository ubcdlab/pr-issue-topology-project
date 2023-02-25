//PR Stack
match (pr:pull_request)-->(pr_2:pull_request)-->(pr_3:pull_request)-->(pr_4:pull_request)-->(pr_5:pull_request)-->(pr_6:pull_request)-->(pr_7:pull_request)
unwind [pr.number, pr_2.number, pr_3.number, pr_4.number, pr_5.number, pr_6.number,pr_7.number] as number_list
with pr, pr_2, pr_3, pr_4, pr_5,pr_6, pr_7, collect(distinct number_list) as number_list
where size(number_list) = 7 and pr.creation_date < pr_2.creation_date < pr_3.creation_date < pr_4.creation_date< pr_5.creation_date < pr_6.creation_date < pr_7.creation_date and pr.user = pr_2.user = pr_3.user = pr_4.user = pr_5.user = pr_6.user = pr_7.user and not (:pull_request)-->(pr) and not (pr_7)-->(:pull_request)
call apoc.path.subgraphAll(pr, {limit: 50, bfs: true })
yield nodes, relationships
return pr, pr_2, pr_3, pr_4, pr_5, pr_6, pr_7, nodes, relationships
//match (pr:pull_request)-->(pr_2:pull_request)-->(pr_3:pull_request)-->(pr_4:pull_request)
//unwind [pr.number, pr_2.number, pr_3.number,pr_4.number] as number_list
//with pr, pr_2, pr_3, pr_4,collect(distinct number_list) as number_list
//where size(number_list) = 4 and pr.creation_date < pr_2.creation_date < pr_3.creation_date <pr_4.creation_date and not (:pull_request)-->(pr) and not (pr_4)-->(:pull_request)
//call apoc.path.subgraphAll(pr, {limit: 50, bfs: true })
//yield nodes, relationships
//return pr, pr_2, pr_3, pr_4, nodes, relationships
//match (pr:pull_request)-->(pr_2:pull_request)-->(pr_3:pull_request)
//unwind [pr.number, pr_2.number, pr_3.number] as number_list
//with pr, pr_2, pr_3, collect(distinct number_list) as number_list
//where size(number_list) = 3 and pr.creation_date < pr_2.creation_date < pr_3.creation_date and not (:pull_request)-->(pr) and not (pr_3)-->(:pull_request)
//call apoc.path.subgraphAll(pr, {limit: 50, bfs: true })
//yield nodes, relationships
//return pr, pr_2, pr_3, nodes, relationships
