call {
with [43529, 92173, 56349, 56350, 56355, 53854, 53855, 53860, 53861, 61030, 57447, 61029, 61035, 68741, 68742, 90257, 68768, 15019, 6833, 3252, 3253, 57529, 6842, 57530, 90300, 90299, 81091, 33989, 33990, 33991, 57552, 87767, 87768, 87784, 6892, 6893, 34030, 34031, 69361, 69362, 69363, 69366, 54016, 54017, 54018, 34058, 3347, 6950, 90932, 90933, 90953, 81229, 81230, 86349, 81234, 43353, 36698, 36699, 43354, 86361, 36703, 60257, 60258, 60259, 69990, 69991, 70008, 39816, 39817, 39818, 83356, 83357, 83358, 28581, 28583, 80808, 80814, 86446, 29104, 29105, 29106, 15802, 15806, 87487, 87496, 87497, 29132, 40420, 40421, 40422, 9199, 92150, 92151, 80890, 57342, 57343] as all_ids // see cypher_scripts/fetch_all_pr_stack_ids
match (hub)-[r]-(pr2:pull_request {status: "merged"})
where ((hub:pull_request and hub.status = "merged") or (hub:issue and hub.status = "closed")) and pr2.creation_date < hub.creation_date and not id(hub) in all_ids and not id(pr2) in all_ids
with hub, collect(distinct pr2) as prs, collect(distinct pr2.user) as users, collect(distinct id(pr2)) as pr_ids
where size(prs) >= 3 and size(users) >= 2
return collect(distinct id(hub))+apoc.coll.toSet(apoc.coll.flatten(collect(pr_ids))) as pr_hub_ids 
}

match (i_1:issue)-[r {labels:"fixes"}]-(pr:pull_request)
where i_1.status = "closed"
with i_1, collect(distinct pr) as pull_requests_1, collect (distinct pr.user) as users, collect(r) as match_relationships_1, max(pr.creation_date) as max_date, min(pr.creation_date) as min_date, pr_hub_ids
where size([p_r in pull_requests_1 where p_r.status="merged"]) = 1 and size([p_r in pull_requests_1 where p_r.status="closed"]) >= 1 and size(pull_requests_1) >= 2 and size(users) > 1 and max_date - min_date <= 604800 // dates are in Unix timestamps so difference is in seconds
with i_1, pull_requests_1, match_relationships_1, [i_1]+pull_requests_1 as competition_match, pr_hub_ids

match (pr1_2:pull_request)-[r_2 {labels:"fixes"}]-(i_2:issue),(pr1_2)-[r_3]-(pr2_2:pull_request),(pr2_2)-[r_4 {labels:"fixes"}]-(i_2)
where not id(i_2) in pr_hub_ids and not id(pr1_2) in pr_hub_ids and not id(pr2_2) in pr_hub_ids and pr1_2.number<>pr2_2.number and i_2.status ="closed" and pr1_2.status="merged" and pr2_2.status="merged" and pr2_2.creation_date > pr1_2.creation_date and (pr1_2 in competition_match or i_2 in competition_match or pr2_2 in competition_match)
with i_1, pull_requests_1, match_relationships_1, pr1_2, i_2, pr2_2, [r_2, r_3, r_4] as match_relationships_2, apoc.coll.intersection(competition_match, [pr1_2,i_2,pr2_2]) as intersection

call apoc.path.subgraphAll(intersection[0], {limit: case 50 > size(pull_requests_1) + 4 when true then 50 when false then size(pull_requests_1) + 4 end, bfs: true })
yield nodes, relationships
return i_1, pull_requests_1, match_relationships_1, pr1_2,  i_2, pr2_2, match_relationships_2, nodes, relationships, intersection as central

