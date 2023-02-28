//PR StackWProportions
match (pr:pull_request)-->(pr_2:pull_request)-->(pr_3:pull_request)
unwind [pr.number, pr_2.number, pr_3.number] as number_list
with pr, pr_2, pr_3, collect(distinct number_list) as number_list
where size(number_list) = 3 and pr.creation_date < pr_2.creation_date < pr_3.creation_date and pr.user = pr_2.user = pr_3.user and not (:pull_request)-->(pr) and not (pr_3)-->(:pull_request)
call apoc.path.subgraphAll(pr, {limit: 50, bfs:true})
yield nodes, relationships
with pr, nodes, [5831, 6950, 12769, 33991, 36703, 40435, 57217, 57447, 57552, 57984, 60259, 61035, 64447, 69605, 81091, 84450, 86446] as known_stacks
with pr, size(collect([i_node in nodes where i_node.type="pull_request" and i_node.number <> pr.number and not id(i_node) in known_stacks])) as not_stack, size(nodes) as len_nodes, nodes
return pr, toFloat(not_stack) / toFloat(len_nodes) as proportion, nodes
