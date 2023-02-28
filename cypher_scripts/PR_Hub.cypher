//PR Hub
match (pr:pull_request)-[r]-(pr2:pull_request)
with pr, collect(distinct pr2) as prs, collect(distinct pr2.user) as users, collect(distinct r) as match_relationships
where size(prs) >= 3 and size(users) >= 2
call apoc.path.subgraphAll(pr, {limit: case 50 > size(prs) when true then 50 when false then size(prs) + 1 end, bfs: true })
yield nodes, relationships
return pr, prs, nodes, relationships, match_relationships
