call {
with [43529, 92173, 56349, 56350, 56355, 53854, 53855, 53860, 53861, 61030, 57447, 61029, 61035, 68741, 68742, 90257, 68768, 15019, 6833, 3252, 3253, 57529, 6842, 57530, 90300, 90299, 81091, 33989, 33990, 33991, 57552, 87767, 87768, 87784, 6892, 6893, 34030, 34031, 69361, 69362, 69363, 69366, 54016, 54017, 54018, 34058, 3347, 6950, 90932, 90933, 90953, 81229, 81230, 86349, 81234, 43353, 36698, 36699, 43354, 86361, 36703, 60257, 60258, 60259, 69990, 69991, 70008, 39816, 39817, 39818, 83356, 83357, 83358, 28581, 28583, 80808, 80814, 86446, 29104, 29105, 29106, 15802, 15806, 87487, 87496, 87497, 29132, 40420, 40421, 40422, 9199, 92150, 92151, 80890, 57342, 57343] as all_ids // see cypher_scripts/fetch_all_pr_stack_ids
match (hub)-[r]-(pr2:pull_request {status: "merged"})
where ((hub:pull_request and hub.status = "merged") or (hub:issue and hub.status = "closed")) and pr2.creation_date < hub.creation_date and not id(hub) in all_ids and not id(pr2) in all_ids
with hub, collect(distinct pr2) as prs, collect(distinct pr2.user) as users, collect(distinct id(pr2)) as pr_ids
where size(prs) >= 3 and size(users) >= 2
return collect(distinct id(hub))+apoc.coll.toSet(apoc.coll.flatten(collect(pr_ids))) as pr_hub_ids 
}

match (pr_1:pull_request)-[r_1 {labels:"fixes"}]-(i_1:issue)
where pr_1.status = "merged"
with pr_1, collect(distinct i_1) as issues_1, collect(distinct r_1) as match_relationships_1, id(pr_1)+collect(distinct id(i_1)) as optimization_match, pr_hub_ids
where size([issue in issues_1 where issue.status="closed"]) > 1
with pr_1, [issue in issues_1 where issue.status="closed"] as closed_issues_1, match_relationships_1, optimization_match, pr_hub_ids

with pr_1, closed_issues_1, match_relationships_1, optimization_match, pr_hub_ids+[80808, 92085] as exclude_ids
match (i_2:issue {status:"closed"})-[r {labels: "fixes"}]-(p_2:pull_request {status: "merged"}), (i2_2:issue {status:"closed"})-[r2]-(p)
optional match (i2)-[r3]-(p2_2:pull_request {status:"merged"})
where p2_2.number <> p.number
with pr_1, closed_issues_1, match_relationships_1, i_2, p_2, i2_2, p2_2, [r, r2, r3] as match_relationships_2, apoc.coll.intersection(optimization_match, [id(i_2), id(p_2), id(i2_2), id(p2_2)]) as intersection, optimization_match
where (i2_2.creation_date > p_2.creation_date or i2_2.creation_date > i_2.creation_date) and i_2.number <> i2_2.number and p_2.number <> p2_2.number and not id(p_2) in exclude_ids and not id(p2_2) in exclude_ids and (id(i_2) in optimization_match or id(p_2) in optimization_match or id(i2_2) in optimization_match or (p2_2 <> null and id(p2_2) in optimization_match))

match (n) where id(n) in intersection 
with pr_1, closed_issues_1, match_relationships_1, i_2, p_2, i2_2, p2_2, match_relationships_2, collect(n) as central

call apoc.path.subgraphAll(central[0], {limit: case 50 > size(closed_issues_1) + 5 when true then 50 when false then size(closed_issues_1) + 5 end, bfs: true })
yield nodes, relationships
return pr_1, closed_issues_1, match_relationships_1, i_2, p_2, i2_2, p2_2, match_relationships_2, nodes, relationships, central

limit 10