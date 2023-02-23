# Neo4J

This project [Neo4J](https://neo4j.com/) as our graph database.

## Importing to Neo4J

Run `python load_all_to_neo4j.py` to generate a list of [GraphML](http://graphml.graphdrawing.org/) files in `graphml_dump/`.

The script recreates all components in all repositories. The script takes edge directions into consideration.

Place these files into the `import` directory of a Neo4J graph database, and run the Cypher query script `cypher_scripts/Import_All_Files`. Alternatively, drag and drop the full database dump (`neo4j.dump` in root directory) into Neo4J.

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

