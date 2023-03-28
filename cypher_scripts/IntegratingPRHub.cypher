//PR Hub
call {
with [43529, 92173, 56349, 56350, 56355, 53854, 53855, 53860, 53861, 61030, 57447, 61029, 61035, 68741, 68742, 90257, 68768, 15019, 6833, 3252, 3253, 57529, 6842, 57530, 90300, 90299, 81091, 33989, 33990, 33991, 57552, 87767, 87768, 87784, 6892, 6893, 34030, 34031, 69361, 69362, 69363, 69366, 54016, 54017, 54018, 34058, 3347, 6950, 90932, 90933, 90953, 81229, 81230, 86349, 81234, 43353, 36698, 36699, 43354, 86361, 36703, 60257, 60258, 60259, 69990, 69991, 70008, 39816, 39817, 39818, 83356, 83357, 83358, 28581, 28583, 80808, 80814, 86446, 29104, 29105, 29106, 15802, 15806, 87487, 87496, 87497, 29132, 40420, 40421, 40422, 9199, 92150, 92151, 80890, 57342, 57343] as all_ids // see cypher_scripts/fetch_all_pr_stack_ids
match (hub)-[r]-(pr2:pull_request {status: "merged"})
where ((hub:pull_request and hub.status = "merged") or (hub:issue and hub.status = "closed")) and pr2.creation_date < hub.creation_date and not id(hub) in all_ids and not id(pr2) in all_ids
with hub, collect(distinct pr2) as prs, collect(distinct pr2.user) as users, collect(distinct id(pr2)) as pr_ids
where size(prs) >= 3 and size(users) >= 2
return collect(distinct id(hub))+apoc.coll.toSet(apoc.coll.flatten(collect(pr_ids))) as known_hubs
}

with [43529, 92173, 56349, 56350, 56355, 53854, 53855, 53860, 53861, 61030, 57447, 61029, 61035, 68741, 68742, 90257, 68768, 15019, 6833, 3252, 3253, 57529, 6842, 57530, 90300, 90299, 81091, 33989, 33990, 33991, 57552, 87767, 87768, 87784, 6892, 6893, 34030, 34031, 69361, 69362, 69363, 69366, 54016, 54017, 54018, 34058, 3347, 6950, 90932, 90933, 90953, 81229, 81230, 86349, 81234, 43353, 36698, 36699, 43354, 86361, 36703, 60257, 60258, 60259, 69990, 69991, 70008, 39816, 39817, 39818, 83356, 83357, 83358, 28581, 28583, 80808, 80814, 86446, 29104, 29105, 29106, 15802, 15806, 87487, 87496, 87497, 29132, 40420, 40421, 40422, 9199, 92150, 92151, 80890, 57342, 57343] as all_ids, known_hubs // see cypher_scripts/fetch_all_pr_stack_ids
match (hub)-[r]-(pr2:pull_request {status: "merged"})
where ((hub:pull_request and hub.status = "merged") or (hub:issue and hub.status = "closed")) and pr2.creation_date < hub.creation_date and not id(hub) in all_ids and not id(pr2) in all_ids
with hub, collect(distinct pr2) as prs, collect(distinct pr2.user) as users, collect(distinct r) as match_relationships, known_hubs
where size(prs) >= 3 and size(users) >= 2
with hub, prs, match_relationships, known_hubs
call apoc.path.subgraphAll(hub, {limit: case 50 > size(prs) when true then 50 when false then size(prs) + 1 end, bfs: true })
yield nodes, relationships
with hub, prs, nodes, relationships, match_relationships, size(collect([i_node in nodes where (i_node.type="pull_request" and hub:pull_request and i_node.status = "merged") or (i_node.type="issue" and hub:issue and i_node.status = "closed") and i_node.number <> hub.number and not id(i_node) in known_hubs])) as not_prhub, size(nodes) as len_nodes
return hub, prs, nodes, relationships, match_relationships, toFloat(not_prhub) / toFloat(len_nodes) as proportion
