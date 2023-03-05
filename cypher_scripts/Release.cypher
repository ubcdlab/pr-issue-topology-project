// Release
match (i:issue {status:"closed"})-[r]-(pr:pull_request{status:"merged"})
where i.creation_date > pr.creation_date
with i, collect(distinct pr) as prs, collect(distinct r) as match_relationships
where size(prs) >= 2
call apoc.path.subgraphAll(i, {limit: case 50 > size(prs) when true then 50 when false then size(prs) + 1 end, bfs: true })
yield nodes, relationships
return i, prs, match_relationships, nodes, relationships
