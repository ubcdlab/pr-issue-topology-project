call {match (i:issue {status: "closed"})-[r {labels:"fixes"}]-(pr:pull_request)
with i, collect(distinct pr) as pull_requests, collect (distinct pr.user) as users, collect(r) as match_relationships, max(pr.creation_date) as max_date, min(pr.creation_date) as min_date
where size([p_r in pull_requests where p_r.status="merged"]) = 1 and size([p_r in pull_requests where p_r.status="closed"]) >= 1 and size(pull_requests) >= 2 and size(users) > 1 and max_date - min_date <= 604800 // dates are in Unix timestamps so difference is in seconds
unwind pull_requests as p_r
return collect(distinct id(i))+collect(distinct id(p_r)) as known

union

call {
with [43529, 92173, 56349, 56350, 56355, 53854, 53855, 53860, 53861, 61030, 57447, 61029, 61035, 68741, 68742, 90257, 68768, 15019, 6833, 3252, 3253, 57529, 6842, 57530, 90300, 90299, 81091, 33989, 33990, 33991, 57552, 87767, 87768, 87784, 6892, 6893, 34030, 34031, 69361, 69362, 69363, 69366, 54016, 54017, 54018, 34058, 3347, 6950, 90932, 90933, 90953, 81229, 81230, 86349, 81234, 43353, 36698, 36699, 43354, 86361, 36703, 60257, 60258, 60259, 69990, 69991, 70008, 39816, 39817, 39818, 83356, 83357, 83358, 28581, 28583, 80808, 80814, 86446, 29104, 29105, 29106, 15802, 15806, 87487, 87496, 87497, 29132, 40420, 40421, 40422, 9199, 92150, 92151, 80890, 57342, 57343] as all_ids // see cypher_scripts/fetch_all_pr_stack_ids
match (hub)-[r]-(pr2:pull_request {status: "merged"})
where ((hub:pull_request and hub.status = "merged") or (hub:issue and hub.status = "closed")) and pr2.creation_date < hub.creation_date and not id(hub) in all_ids and not id(pr2) in all_ids
with hub, collect(distinct pr2) as prs, collect(distinct pr2.user) as users, collect(distinct id(pr2)) as pr_ids
where size(prs) >= 3 and size(users) >= 2
return collect(distinct id(hub))+apoc.coll.toSet(apoc.coll.flatten(collect(pr_ids))) as known_hubs
}

with known_hubs
with known_hubs+[80808, 92085] as exclude_ids
match (i:issue {status:"closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (i2:issue {status:"closed"})-[r2]-(p), (i2)-[r3]-(p2:pull_request {status:"merged"})
where (i2.creation_date > p.creation_date or i2.creation_date > i.creation_date) and i.number <> i2.number and p.number <> p2.number and not id(p) in exclude_ids and not id(p2) in exclude_ids
return collect(distinct id(i))+collect(distinct id(p))+collect(distinct id(i2))+collect(distinct id(p2)) as known

union

match (i:issue {status:"closed"})-[r {labels: "fixes"}]-(p:pull_request {status: "merged"}), (i2:issue)-[r2]-(p)
where i2.creation_date > p.creation_date and i.number <> i2.number
return collect(distinct id(i))+collect(distinct id(p))+collect(distinct id(i2)) as known

union 

match (i:issue {status: "closed"})-[r {labels: "fixes"}]-(pr:pull_request), (i)-[r2 {labels: "fixes"}]-(pr_2:pull_request)
where not (pr)--(pr_2) and pr.number <> pr_2.number and ((pr.status = "closed" and (pr)--(pr_2) and pr_2.status="merged") or pr.status <> "closed")
with i, collect(distinct pr)+collect(distinct pr_2) as pull_requests, collect(distinct r)+collect(distinct r2) as match_relationships, collect(distinct id(i))+collect(distinct id(pr))+collect(distinct id(pr_2)) as known_decomposition
where size(pull_requests) > 1 and size([p in pull_requests where p.status = "merged"]) >= toFloat(size(pull_requests))/ toFloat(2)
return apoc.coll.toSet(apoc.coll.flatten(collect(known_decomposition))) as known 

union 

return [43529, 92173, 56349, 56350, 56355, 53854, 53855, 53860, 53861, 61030, 57447, 61029, 61035, 68741, 68742, 90257, 68768, 15019, 6833, 3252, 3253, 57529, 6842, 57530, 90300, 90299, 81091, 33989, 33990, 33991, 57552, 87767, 87768, 87784, 6892, 6893, 34030, 34031, 69361, 69362, 69363, 69366, 54016, 54017, 54018, 34058, 3347, 6950, 90932, 90933, 90953, 81229, 81230, 86349, 81234, 43353, 36698, 36699, 43354, 86361, 36703, 60257, 60258, 60259, 69990, 69991, 70008, 39816, 39817, 39818, 83356, 83357, 83358, 28581, 28583, 80808, 80814, 86446, 29104, 29105, 29106, 15802, 15806, 87487, 87496, 87497, 29132, 40420, 40421, 40422, 9199, 92150, 92151, 80890, 57342, 57343] as known // see cypher_scripts/fetch_all_pr_stack_ids

union 

match (pr:pull_request {status: "merged"})-[r {labels:"fixes"}]-(i:issue)
with pr, collect(distinct i) as issues, collect(distinct r) as match_relationships
where size([issue in issues where issue.status="closed"]) > 1
unwind issues as i
return collect(distinct id(pr))+collect(distinct id(i)) as known 

union 

match (i:issue)-[r {labels:"duplicate"}]-(i2:issue)
where i2.creation_date > i.creation_date and i2.user <> i.user
with i, collect(distinct i2) as spoke_issues, collect(distinct r) as match_relationships, collect(distinct id(i))+collect(distinct id(i2)) as known_dups
where size(spoke_issues) > 1
return apoc.coll.toSet(apoc.coll.flatten(collect(known_dups))) as known

union

call {
with [43529, 92173, 56349, 56350, 56355, 53854, 53855, 53860, 53861, 61030, 57447, 61029, 61035, 68741, 68742, 90257, 68768, 15019, 6833, 3252, 3253, 57529, 6842, 57530, 90300, 90299, 81091, 33989, 33990, 33991, 57552, 87767, 87768, 87784, 6892, 6893, 34030, 34031, 69361, 69362, 69363, 69366, 54016, 54017, 54018, 34058, 3347, 6950, 90932, 90933, 90953, 81229, 81230, 86349, 81234, 43353, 36698, 36699, 43354, 86361, 36703, 60257, 60258, 60259, 69990, 69991, 70008, 39816, 39817, 39818, 83356, 83357, 83358, 28581, 28583, 80808, 80814, 86446, 29104, 29105, 29106, 15802, 15806, 87487, 87496, 87497, 29132, 40420, 40421, 40422, 9199, 92150, 92151, 80890, 57342, 57343] as all_ids // see cypher_scripts/fetch_all_pr_stack_ids
match (hub)-[r]-(pr2:pull_request {status: "merged"})
where ((hub:pull_request and hub.status = "merged") or (hub:issue and hub.status = "closed")) and pr2.creation_date < hub.creation_date and not id(hub) in all_ids and not id(pr2) in all_ids
with hub, collect(distinct pr2) as prs, collect(distinct pr2.user) as users, collect(distinct id(pr2)) as pr_ids
where size(prs) >= 3 and size(users) >= 2
return collect(distinct id(hub))+apoc.coll.toSet(apoc.coll.flatten(collect(pr_ids))) as all_ids 
}

with all_ids
match (pr1:pull_request)-[r {labels:"fixes"}]-(i:issue),(pr1)-[r2]-(pr2:pull_request),(pr2)-[r3 {labels:"fixes"}]-(i)
where not id(i) in all_ids and not id(pr1) in all_ids and not id(pr2) in all_ids and pr1.number<>pr2.number and i.status ="closed" and pr1.status="merged" and pr2.status="merged" and pr2.creation_date > pr1.creation_date
return collect(distinct id(i))+collect(distinct id(pr1))+collect(distinct id(pr2)) as known

union

with [43529, 92173, 56349, 56350, 56355, 53854, 53855, 53860, 53861, 61030, 57447, 61029, 61035, 68741, 68742, 90257, 68768, 15019, 6833, 3252, 3253, 57529, 6842, 57530, 90300, 90299, 81091, 33989, 33990, 33991, 57552, 87767, 87768, 87784, 6892, 6893, 34030, 34031, 69361, 69362, 69363, 69366, 54016, 54017, 54018, 34058, 3347, 6950, 90932, 90933, 90953, 81229, 81230, 86349, 81234, 43353, 36698, 36699, 43354, 86361, 36703, 60257, 60258, 60259, 69990, 69991, 70008, 39816, 39817, 39818, 83356, 83357, 83358, 28581, 28583, 80808, 80814, 86446, 29104, 29105, 29106, 15802, 15806, 87487, 87496, 87497, 29132, 40420, 40421, 40422, 9199, 92150, 92151, 80890, 57342, 57343] as all_ids // see cypher_scripts/fetch_all_pr_stack_ids
match (hub)-[r]-(pr2:pull_request {status: "merged"})
where ((hub:pull_request and hub.status = "merged") or (hub:issue and hub.status = "closed")) and pr2.creation_date < hub.creation_date and not id(hub) in all_ids and not id(pr2) in all_ids
with hub, collect(distinct pr2) as prs, collect(distinct pr2.user) as users, collect(distinct id(pr2)) as pr_ids
where size(prs) >= 3 and size(users) >= 2
return collect(distinct id(hub))+apoc.coll.toSet(apoc.coll.flatten(collect(pr_ids))) as known
}

return size(apoc.coll.toSet(apoc.coll.flatten(collect(known))))
