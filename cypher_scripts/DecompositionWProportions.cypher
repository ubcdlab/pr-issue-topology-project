//DecompositionWProportions
match (i:issue {status: "closed"})-[r {labels: "fixes"}]-(pr:pull_request {status: "merged"})
with i, collect(pr) as pull_requests
where size(pull_requests) > 1
with i, pull_requests, [584, 1031, 3165, 3195, 3800, 4390, 7819, 11063, 11118, 21743, 23666, 23708, 25996, 26059, 26814, 26475, 26618, 26698, 26812, 26917, 26926, 27066, 27324, 27511, 29352, 30009, 32048, 35229, 33036, 33072, 33497, 34223, 33243, 33281, 54847, 62122, 64223, 64427, 64397, 64398, 64737, 64764, 66140, 68424, 70011, 79841, 80037, 79696, 79962, 79809, 79884, 80453, 85263, 86701, 86719, 89477] as known_decomposition
call apoc.path.subgraphAll(i, {limit: case 50 > size(pull_requests) when true then 50 when false then size(pull_requests) + 1 end, bfs: true })
yield nodes, relationships
return distinct i, size(collect([i_node in nodes where i_node.type="issue" and i_node.status="closed" and i_node.number <> i.number and not id(i_node) in known_decomposition]))