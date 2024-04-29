# Neo4J

This project [Neo4J](https://neo4j.com/) as our graph database.

## Importing to Neo4J

Run `python load_all_to_neo4j.py` to generate a list of [GraphML](http://graphml.graphdrawing.org/) files in `graphml_dump/`.

The script recreates all components in all repositories. The script takes edge directions into consideration.

Place these files into the `import` directory of a Neo4J graph database, and run the Cypher query script `cypher_scripts/Import_All_Files.cypher`. Alternatively, drag and drop the full database dump (`neo4j.dump` in root directory) into Neo4J.

The attributes available in the database are:

- `type`: one of `pull_request` or `issue`
- `status`: one of `merged`, `closed`, or `open`
- `repository`: in `user/repo` format
- `creation_date`: Unix timestamp
- `updated_at`: Unix timestamp
- `closed_at`: Unix timestamp or 0 if node's `status` is `open`.
- `number`: node identifier, same as pull request or issue number on GitHub
- `link_type`: only for edges; one of `fixes`, `duplicate`, or `other`
- `user`: the GitHub username of the user that created the node (or for edges, the comment linking the two nodes)
- `user_url`: URL to GitHub page of user
- `url`: URL to node's GitHub page; similarly, `link_url` links to the mentioning issue's GitHub page

## Querying

Copy-paste one of the topology pattern scripts in `cypher_scripts/` in the Neo4J Browser to return results.

Our queries will visualize both the matches and the components the matches were found in.

Neo4J will match subgraphs separately. For example, if a query is for an issue linked to a pull request, and there is one issue linking to many pull requests, each issue / pull request match is returned separately. Neo4J also may return duplicate nodes if running a `collect`, so ensure `collect(distinct ...)` is used instead. This may be salient when returning `count`s.

Take care when using Neo4J `collect` statements to collect information about _all_ instances. If used like so, it will return only the distinct IDs within a match:

```
with i, collect(distinct id(i)) as ids
```

To get all IDs over all matches, use a subquery call first. The result can then be included into the scope of the remaining query with `with`.

```
match (i)
where ...
return collect(distinct id(i)) as ids
```

## Excluding Matches

Some topologies require other topologies to be excluded before they can be matched. For example, matches of Consequence 2 will all contain matches for Consequence 1, so matches of Consequence 2 need to be excluded before querying for Consequence 1 to ensure their results are mutually exclusive.

This can be done by collecting a list of node IDs (Neo4J-assigned) for all known matches of a topology. Because of the way Neo4J's `collect` works, the query for the excluded topology must be called in the query for the topology to be matched.

- First, run the match for the excluded topology and collect all node IDs (i.e. `return collect(distinct id(i))+collect(distinct id(p)) as exclude_ids`)
- Then, run the match for the topology to be matched, and assert none of its node IDs are in the list of `exclude_ids`

This technique is used in several queries, including for excluding Dependent PRs from PR Hubs and PR Hubs from Improvements. Note how the pattern dependencies 'chain' into queries: the query for exclusion of Dependent PRs from PR Hubs must also be executed in the Improvements query.

## Dependent PR Query Generation

The Dependent PR topology is unique in that Neo4J does not have a feature to match a path of unspecified length while specifying properties of nodes on that path, so queries are generated with a script.

`python -m cypher_scripts.generate_pr_stack --size=[size]` will generate a query for a stack of the specified size, and save it to `cypher_scripts/PR_Stack_Gen.cypher`.

The same query generation function is used in `cypher_scripts/fetch_all_pr_stack_ids.py` to statically fetch all IDs of nodes in a Dependent PR topology. The script prints the set of node IDs, as well as saving them to `cypher_scripts/all_ids_dump`. This makes the PR Hub and Improvement queries more efficient as the list of IDs can be loaded statically without running many iterations of the Dependent PR subquery.
