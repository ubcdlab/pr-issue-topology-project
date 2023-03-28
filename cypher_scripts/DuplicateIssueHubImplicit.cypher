match (i:issue)--(i2:issue)
where i2.creation_date > i.creation_date and i.user <> i2.user and not (i)-[{labels:"duplicate"}]-(i2)
with i, collect(distinct i2) as spoke_issues
where size(spoke_issues) > 1
call apoc.path.subgraphAll(i, {limit: case 50 > size(spoke_issues) when true then 50 when false then size(spoke_issues) + 1 end, bfs: true })
yield nodes, relationships
return i, spoke_issues, nodes, relationships
