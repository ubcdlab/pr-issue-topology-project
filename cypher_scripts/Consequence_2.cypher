// Consequence-2
call {
with [80808, 92085] as exclude_ids
match (i:issue {status:"closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (i2:issue {status:"closed"})-[r2]-(p), (i2)-[r3]-(p2:pull_request {status:"merged"})
where (i2.creation_date > p.creation_date or i2.creation_date > i.creation_date) and i.number <> i2.number and p.number <> p2.number and not id(p) in exclude_ids and not id(p2) in exclude_ids
return collect(distinct id(i)) as known_consq
}

call {
with [43529, 92173, 56349, 56350, 56355, 53854, 53855, 53860, 53861, 61030, 57447, 61029, 61035, 68741, 68742, 90257, 68768, 15019, 6833, 3252, 3253, 57529, 6842, 57530, 90300, 90299, 81091, 33989, 33990, 33991, 57552, 87767, 87768, 87784, 6892, 6893, 34030, 34031, 69361, 69362, 69363, 69366, 54016, 54017, 54018, 34058, 3347, 6950, 90932, 90933, 90953, 81229, 81230, 86349, 81234, 43353, 36698, 36699, 43354, 86361, 36703, 60257, 60258, 60259, 69990, 69991, 70008, 39816, 39817, 39818, 83356, 83357, 83358, 28581, 28583, 80808, 80814, 86446, 29104, 29105, 29106, 15802, 15806, 87487, 87496, 87497, 29132, 40420, 40421, 40422, 9199, 92150, 92151, 80890, 57342, 57343] as all_ids // see cypher_scripts/fetch_all_pr_stack_ids
match (hub)-[r]-(pr2:pull_request {status: "merged"})
where ((hub:pull_request and hub.status = "merged") or (hub:issue and hub.status = "closed")) and pr2.creation_date < hub.creation_date and not id(hub) in all_ids and not id(pr2) in all_ids
with hub, collect(distinct pr2) as prs, collect(distinct pr2.user) as users, collect(distinct id(pr2)) as pr_ids
where size(prs) >= 3 and size(users) >= 2
return collect(distinct id(hub))+apoc.coll.toSet(apoc.coll.flatten(collect(pr_ids))) as known_hubs
}

with known_hubs+[80808, 92085] as exclude_ids, known_consq
match (i:issue {status:"closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (i2:issue {status:"closed"})-[r2]-(p), (i2)-[r3]-(p2:pull_request {status:"merged"})
where (i2.creation_date > p.creation_date or i2.creation_date > i.creation_date) and i.number <> i2.number and p.number <> p2.number and not id(p) in exclude_ids and not id(p2) in exclude_ids and not id(i) in exclude_ids and not id(i2) in exclude_ids
with i, p, i2, p2, [r,r2,r3] as match_relationships, known_consq
call apoc.path.subgraphAll(i, {limit: 50, bfs: true })
yield nodes, relationships
with i, p, i2, p2, nodes, relationships, match_relationships, size(collect([i_node in nodes where i_node.type="issue" and i_node.status="closed" and i_node.number <> i.number and i_node.number <> i2.number and not id(i_node) in known_consq])) as not_consq, size(nodes) as len_nodes
return i, p, i2, p2, nodes, relationships, match_relationships, toFloat(not_consq) / toFloat(len_nodes) as proportion
