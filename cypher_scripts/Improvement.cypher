//Improvement
call {
// PR hubs
with [27139, 87556, 87557, 43529, 87565, 92173, 92178, 56349, 56350, 56355, 53854, 53855, 53860, 53861, 61030, 57447, 61029, 61035, 28287, 28288, 68741, 68742, 90257, 28312, 68768, 15019, 6833, 3252, 3253, 57529, 6842, 57530, 90300, 90299, 81091, 33989, 33990, 33991, 57552, 87767, 87768, 87784, 6892, 6893, 34030, 34031, 69361, 69362, 69363, 69366, 54016, 54017, 54018, 34058, 7436, 7437, 3347, 7445, 6950, 90932, 90933, 27134, 90953, 27135, 81229, 81230, 86349, 81234, 43353, 36698, 36699, 43354, 86361, 36703, 60257, 60258, 60259, 69990, 69991, 70008, 39816, 39817, 39818, 83356, 83357, 83358, 28581, 28583, 80808, 80814, 86446, 29104, 29105, 29106, 92083, 92085, 15802, 15806, 87487, 87496, 87497, 29132, 14809, 14811, 14816, 40420, 40421, 40422, 9199, 92150, 92151, 80890, 57342, 57343] as all_ids // see cypher_scripts/fetch_all_pr_stack_ids
match (pr:pull_request)-[r]-(pr2:pull_request)
where pr2.creation_date < pr.creation_date and not id(pr) in all_ids and not id(pr2) in all_ids
with pr, collect(distinct pr2) as prs, collect(distinct pr2.user) as users
where size(prs) >= 3 and size(users) >= 2
with collect(distinct id(pr)) as all_ids

// release
match (i:issue {status:"closed"})-[r]-(pr:pull_request{status:"merged"})
where i.creation_date > pr.creation_date
with i, collect(distinct id(pr)) as prs, all_ids
where size(prs) >= 2
return all_ids+id(i)+prs as all_ids
}
match (pr1:pull_request)-[r {labels:"fixes"}]-(i:issue),(pr1)-[r2]-(pr2:pull_request),(pr2)-[r3 {labels:"fixes"}]-(i)
where not id(i) in all_ids and not id(pr1) in all_ids and not id(pr2) in all_ids and pr1.number<>pr2.number and i.status ="closed" and pr1.status="merged" and pr2.status="merged" and pr2.creation_date > pr1.creation_date
with i, pr1, pr2, [r,r2,r3] as match_relationships, collect(distinct id(i)) as known_improvement
call apoc.path.subgraphAll(i, {limit: 50, bfs:true})
yield nodes, relationships
with i, pr1, pr2, nodes, relationships, match_relationships, size(collect([i_node in nodes where i_node.type="issue" and i_node.status="closed" and i_node.number <> i.number and not id(i_node) in known_improvement])) as not_imp, size(nodes) as len_nodes
return i, pr1, pr2, nodes, relationships, match_relationships, toFloat(not_imp) / toFloat(len_nodes) as proportion
